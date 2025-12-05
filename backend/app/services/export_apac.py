from datetime import datetime
from typing import List, Dict
import unicodedata

from app.exports.field_map_apac_2025 import HEADER_APAC_2025, CORPO_APAC_2025, PROC_APAC_2025

HEADER_LEN = 139  # sem CRLF
CORPO_LEN = 538   # sem CRLF
PROC_LEN = 99     # sem CRLF


def _fill_fields(buffer: List[str], field_map: List[Dict], values: Dict[str, str]):
    for field in field_map:
        name = field["name"]
        start = field["start"] - 1
        length = field["length"]
        default = field.get("default", "")
        required = field.get("required", False)
        pad = field.get("pad", " ")
        value = values.get(name, default)
        if value is None:
            value = ""
        if required and (str(value).strip() == ""):
            raise ValueError(f"Campo obrigatorio ausente: {name}")
        value_str = str(value)
        if pad == "0":
            value_str = value_str.zfill(length)
        else:
            value_str = value_str.ljust(length)
        buffer[start:start + length] = list(value_str[:length])
    return buffer


def _ensure_crlf(line_body: str, expected_len: int) -> str:
    """
    Enforce CRLF terminator and validate body length (without CRLF).
    """
    trimmed = line_body.rstrip("\r\n")
    if len(trimmed) != expected_len:
        raise ValueError(f"Registro APAC fora do tamanho esperado: {len(trimmed)} != {expected_len}")
    return trimmed[:expected_len] + "\r\n"


def calc_checksum_apac(procedimentos: List[Dict[str, str]], numero_apac: str) -> int:
    """
    Soma codigos base + quantidades + numero da APAC (uma vez), mod 1111, controle = resto + 1111.
    """
    soma = 0
    numero_apac_int = int("".join(ch for ch in numero_apac if ch.isdigit()) or 0)
    soma += numero_apac_int
    for proc in procedimentos:
        codigo_raw = proc.get("codigo", "0") or "0"
        codigo_digits = "".join(ch for ch in codigo_raw if ch.isdigit())
        codigo_base = codigo_digits[:-1] if len(codigo_digits) > 9 else codigo_digits
        quantidade = int(proc.get("quantidade", 0))
        soma += int(codigo_base or 0)
        soma += quantidade
    resto = soma % 1111
    controle = resto + 1111
    if controle < 1111 or controle > 2221:
        raise ValueError("Checksum fora do dominio 1111..2221")
    return controle


def build_header(competencia: str, qtd_apac: int, orgao: str, sigla: str, cnpj: str, destino: str,
                 versao: str, checksum: int) -> str:
    buffer = [" "] * HEADER_LEN
    values = {
        "competencia": competencia,
        "quantidade_apac": qtd_apac,
        "checksum": checksum,
        "orgao": orgao,
        "sigla": sigla,
        "cnpj": cnpj,
        "destino": destino,
        "data_geracao": datetime.utcnow().strftime("%Y%m%d"),
        "versao": versao,
    }
    _fill_fields(buffer, HEADER_APAC_2025, values)
    return _ensure_crlf("".join(buffer), HEADER_LEN)


def _normalize_ascii(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    return "".join(ch for ch in normalized if ord(ch) < 128)


def build_corpo(registro: Dict[str, str]) -> str:
    if not registro.get("cns_paciente"):
        raise ValueError("CNS do paciente obrigatorio na APAC")
    buffer = [" "] * CORPO_LEN
    # normalizar textos antes de preencher
    valores = {k: (_normalize_ascii(v) if isinstance(v, str) else v) for k, v in registro.items()}
    # regras condicionais: etnia so se raca_cor == "05"
    if valores.get("apa_raca_cor") != "05":
        valores["apa_etnia"] = ""
    # dt obito/alta so se motsaida indicar obito (07,08) ou alta (01/02/03)
    if valores.get("apa_motsaida") not in {"07", "08", "01", "02", "03"}:
        valores["apa_dtobitoalta"] = ""
    _fill_fields(buffer, CORPO_APAC_2025, valores)
    return _ensure_crlf("".join(buffer), CORPO_LEN)


def build_proc(registro: Dict[str, str]) -> str:
    buffer = [" "] * PROC_LEN
    _fill_fields(buffer, PROC_APAC_2025, registro)
    return _ensure_crlf("".join(buffer), PROC_LEN)


def gerar_arquivo(competencia: str, orgao: str, sigla: str, cnpj: str, destino: str, versao: str,
                  corpo: Dict[str, str], procedimentos: List[Dict[str, str]]) -> str:
    numero_apac = corpo.get("numero_apac", "0")
    checksum = calc_checksum_apac(procedimentos, numero_apac)
    header = build_header(competencia, 1, orgao, sigla, cnpj, destino, versao, checksum)
    main = build_corpo(corpo)
    procs = [build_proc({**p, "competencia": competencia}) for p in procedimentos]
    arquivo = header + main + "".join(procs)
    if len(header.rstrip("\r\n")) != HEADER_LEN:
        raise ValueError("Header APAC fora do tamanho oficial")
    if len(main.rstrip("\r\n")) != CORPO_LEN:
        raise ValueError("Corpo APAC fora do tamanho oficial")
    if any(len(p.rstrip("\r\n")) != PROC_LEN for p in procs):
        raise ValueError("Registro procedimento APAC fora do tamanho oficial")
    return arquivo
