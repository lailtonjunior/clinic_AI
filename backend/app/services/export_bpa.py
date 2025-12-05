import math
from typing import List, Dict

from app.exports.field_map_bpa_2025 import HEADER_BPA_2025, LINHA_BPA_2025, TRAILER_BPA_2025

HEADER_LEN = 132  # sem CRLF
LINE_LEN = 352    # sem CRLF
TRAILER_LEN = 132  # sem CRLF


def _fill_fields(buffer: List[str], field_map: List[Dict], values: Dict[str, str]):
    """
    Preenche o buffer de linha a partir do mapa oficial de campos.
    """
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
    Garante terminador CRLF e valida comprimento (sem CRLF).
    """
    trimmed = line_body.rstrip("\r\n")
    if len(trimmed) != expected_len:
        raise ValueError(f"Registro BPA fora do tamanho esperado: {len(trimmed)} != {expected_len}")
    return trimmed[:expected_len] + "\r\n"


def calc_checksum_bpa(procedures: List[Dict[str, str]]) -> int:
    """
    Soma codigo (sem DV) + quantidade de cada linha, mod 1111, controle = resto + 1111.
    """
    soma = 0
    for proc in procedures:
        codigo_raw = proc.get("procedimento", "") or ""
        codigo_digits = "".join(ch for ch in codigo_raw if ch.isdigit())
        codigo_base = codigo_digits[:9]  # sem DV
        quantidade = int(proc.get("quantidade", 0))
        soma += int(codigo_base) if codigo_base else 0
        soma += quantidade
    resto = soma % 1111
    controle = resto + 1111
    if controle < 1111 or controle > 2221:
        raise ValueError("Checksum fora do dominio 1111..2221")
    return controle


def build_header(competencia: str, quantidade_linhas: int, quantidade_folhas: int, orgao_nome: str,
                 orgao_sigla: str, cnpj: str, orgao_destino: str, destino: str, versao: str,
                 checksum: int) -> str:
    buffer = [" "] * HEADER_LEN
    values = {
        "competencia": competencia,
        "quantidade_linhas": quantidade_linhas,
        "quantidade_folhas": quantidade_folhas,
        "checksum": checksum,
        "orgao_nome": orgao_nome,
        "orgao_sigla": orgao_sigla,
        "cnpj": cnpj,
        "orgao_destino": orgao_destino,
        "destino": destino,
        "versao": versao,
    }
    _fill_fields(buffer, HEADER_BPA_2025, values)
    return _ensure_crlf("".join(buffer), HEADER_LEN)


def build_linha(procedimento: Dict[str, str], folha: int | None = None, sequencia: int | None = None) -> str:
    cns_pac = procedimento.get("cns_paciente")
    cpf_pac = procedimento.get("cpf_paciente")
    if cns_pac and cpf_pac:
        raise ValueError("CNS pac OU CPF pac, nunca ambos")
    if not cns_pac and not cpf_pac:
        raise ValueError("CNS ou CPF deve ser informado")
    buffer = [" "] * LINE_LEN
    _fill_fields(buffer, LINHA_BPA_2025, {
        "cnes": procedimento.get("cnes", ""),
        "competencia": procedimento.get("competencia", ""),
        "cns_prof": procedimento.get("cns_prof", ""),
        "cbo": procedimento.get("cbo", ""),
        "data_atendimento": procedimento.get("data_atendimento", ""),
        "procedimento": procedimento.get("procedimento", ""),
        "cns_paciente": cns_pac or "",
        "cpf_paciente": cpf_pac or "",
        "sexo": procedimento.get("sexo", ""),
        "cid": procedimento.get("cid", ""),
        "idade": str(procedimento.get("idade", "")),
        "quantidade": str(procedimento.get("quantidade", "")),
        "valor": str(int(float(procedimento.get("valor", 0)) * 100)).zfill(10),
        "prd_flh": folha if folha is not None else "",
        "prd_seq": sequencia if sequencia is not None else "",
    })
    return "".join(buffer) + "\r\n"


def build_trailer(total_procs: int, valor_total: float, checksum: int) -> str:
    buffer = [" "] * TRAILER_LEN
    _fill_fields(buffer, TRAILER_BPA_2025, {
        "total_procedimentos": total_procs,
        "valor_total": f"{valor_total:.2f}".replace(".", ""),
        "checksum": checksum,
    })
    return "".join(buffer) + "\r\n"


def gerar_arquivo(competencia: str, orgao: str, sigla: str, cnpj: str, destino: str, versao: str,
                  procedimentos: List[Dict[str, str]]) -> str:
    checksum = calc_checksum_bpa(procedimentos)
    quantidade_folhas = math.ceil(len(procedimentos) / 20) if procedimentos else 1
    header = build_header(competencia, len(procedimentos), quantidade_folhas, orgao, sigla, cnpj, "SES", destino, versao, checksum)
    linhas = []
    for idx, p in enumerate(procedimentos):
        folha = (idx // 20) + 1
        sequencia = (idx % 20) + 1
        linhas.append(build_linha(p, folha=folha, sequencia=sequencia))
    trailer = build_trailer(len(procedimentos), sum([float(p.get("valor", 0)) for p in procedimentos]), checksum)
    arquivo = header + "".join(linhas) + trailer
    if any(len(l.rstrip("\r\n")) != LINE_LEN for l in linhas):
        raise ValueError("Linha BPA-I fora do tamanho oficial")
    if len(header.rstrip("\r\n")) != HEADER_LEN:
        raise ValueError("Header BPA-I fora do tamanho oficial")
    if len(trailer.rstrip("\r\n")) != TRAILER_LEN:
        raise ValueError("Trailer BPA-I fora do tamanho oficial")
    return arquivo
