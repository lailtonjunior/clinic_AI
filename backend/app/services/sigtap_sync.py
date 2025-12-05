import csv
import io
import zipfile
from datetime import datetime
from typing import Callable, Dict, Iterable, List, Optional, Tuple

import httpx
from sqlalchemy import and_, func, or_, select

from app import models
from app.core.config import settings

CSV_DELIMITER = ";"


def _normalize_bool(value: Optional[str]) -> bool:
    if value is None:
        return False
    normalized = str(value).strip().upper()
    return normalized in {"S", "SIM", "1", "TRUE", "T", "Y"}


def _normalize_int(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def _normalize_valor(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip().replace(".", "").replace(",", ".")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _strip(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _iter_csv_rows(file_bytes: bytes) -> Iterable[Dict[str, str]]:
    decoded = file_bytes.decode("latin-1")
    reader = csv.DictReader(io.StringIO(decoded), delimiter=CSV_DELIMITER)
    for row in reader:
        yield {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}


def _find_first_matching(zf: zipfile.ZipFile, keywords: Tuple[str, ...]) -> Optional[str]:
    for name in zf.namelist():
        lower = name.lower()
        if lower.endswith(".csv") and any(key in lower for key in keywords):
            return name
    return None


def _parse_procedimento_rows(proc_rows: Iterable[Dict[str, str]], regra_por_codigo: Dict[str, Dict[str, str]], competencia: str) -> List[Dict]:
    registros: List[Dict] = []
    for row in proc_rows:
        codigo = row.get("CO_PROCEDIMENTO") or row.get("codigo") or ""
        codigo = codigo.zfill(10)
        if not codigo.strip():
            continue
        descricao = (row.get("NO_PROCEDIMENTO") or row.get("descricao") or "").strip()
        regra_extra = regra_por_codigo.get(codigo, {})
        sexo_raw = row.get("TP_SEXO") or regra_extra.get("TP_SEXO") or "A"
        idade_min = _normalize_int(regra_extra.get("NU_IDADE_MINIMA") or row.get("NU_IDADE_MINIMA") or row.get("IDADE_MIN"))
        idade_max = _normalize_int(regra_extra.get("NU_IDADE_MAXIMA") or row.get("NU_IDADE_MAXIMA") or row.get("IDADE_MAX"))
        doc_paciente = (
            regra_extra.get("DOC_PACIENTE")
            or row.get("DOC_PACIENTE")
            or "AMBOS_PERMITIDOS"
        )
        doc_paciente = doc_paciente.upper()
        sexo_permitido = (sexo_raw or "A").upper()
        vigencia_inicio = (
            _strip(regra_extra.get("DT_INICIO"))
            or _strip(row.get("DT_INICIO"))
            or _strip(row.get("DT_COMPETENCIA"))
            or competencia
        )
        vigencia_fim = _strip(regra_extra.get("DT_FIM") or row.get("DT_FIM"))

        registro = {
            "codigo": codigo,
            "descricao": descricao,
            "valor": _normalize_valor(row.get("VL_PROCEDIMENTO") or row.get("valor")),
            "regras": {
                "complexidade": row.get("CO_COMPLEXIDADE") or regra_extra.get("CO_COMPLEXIDADE"),
                "modalidade": row.get("CO_MODALIDADE") or regra_extra.get("CO_MODALIDADE"),
            },
            "vigencia": competencia,
            "exige_cid": _normalize_bool(regra_extra.get("EXIGE_CID") or row.get("EXIGE_CID")),
            "exige_apac": _normalize_bool(regra_extra.get("EXIGE_APAC") or row.get("EXIGE_APAC")),
            "doc_paciente": doc_paciente,
            "sexo_permitido": sexo_permitido,
            "idade_min": idade_min,
            "idade_max": idade_max,
            "vigencia_inicio": vigencia_inicio,
            "vigencia_fim": vigencia_fim,
        }
        registros.append(registro)
    return registros


def _montar_regra_map(regra_rows: Iterable[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    regras: Dict[str, Dict[str, str]] = {}
    for row in regra_rows:
        codigo = (row.get("CO_PROCEDIMENTO") or row.get("codigo") or "").zfill(10)
        if not codigo.strip():
            continue
        regras[codigo] = row
    return regras


class TabelaSIGTAPRepository:
    def __init__(self, session):
        self.session = session

    def competencia_importada(self, competencia: str) -> bool:
        stmt = select(func.count()).select_from(models.TabelaSIGTAP).where(
            or_(models.TabelaSIGTAP.vigencia == competencia, models.TabelaSIGTAP.vigencia_inicio == competencia)
        )
        return self.session.execute(stmt).scalar_one() > 0

    def salvar(self, item: dict) -> bool:
        vigencia_inicio = item.get("vigencia_inicio") or item.get("vigencia")
        exists_stmt = select(models.TabelaSIGTAP).where(
            and_(
                models.TabelaSIGTAP.codigo == item["codigo"],
                models.TabelaSIGTAP.vigencia_inicio == vigencia_inicio,
            )
        )
        if self.session.scalars(exists_stmt).first():
            return False

        obj = models.TabelaSIGTAP(
            codigo=item["codigo"],
            descricao=item["descricao"],
            valor=item.get("valor"),
            regras=item.get("regras", {}),
            vigencia=item.get("vigencia"),
            exige_cid=item.get("exige_cid", False),
            exige_apac=item.get("exige_apac", False),
            doc_paciente=item.get("doc_paciente", "AMBOS_PERMITIDOS"),
            sexo_permitido=item.get("sexo_permitido", "A"),
            idade_min=item.get("idade_min"),
            idade_max=item.get("idade_max"),
            vigencia_inicio=vigencia_inicio,
            vigencia_fim=item.get("vigencia_fim"),
        )
        self.session.add(obj)
        self.session.commit()
        return True

    def ultima_competencia(self) -> Optional[str]:
        stmt = select(func.max(models.TabelaSIGTAP.vigencia))
        return self.session.execute(stmt).scalar_one()

    def total_registros(self) -> int:
        stmt = select(func.count()).select_from(models.TabelaSIGTAP)
        return self.session.execute(stmt).scalar_one()

    def existe_codigo(self, codigo: str) -> bool:
        stmt = select(func.count()).select_from(models.TabelaSIGTAP).where(models.TabelaSIGTAP.codigo == codigo)
        return self.session.execute(stmt).scalar_one() > 0


class SIGTAPSyncService:
    def __init__(
        self,
        repository: TabelaSIGTAPRepository,
        base_url: Optional[str] = None,
        fetcher: Optional[Callable[[str], bytes]] = None,
    ):
        self.repository = repository
        self.base_url = base_url or settings.sigtap_base_url
        self.fetcher = fetcher

    def _build_urls(self, competencia: str) -> List[str]:
        base = self.base_url.rstrip("/")
        if "{competencia}" in base:
            return [base.format(competencia=competencia)]
        candidates = [
            f"SIGTAP_{competencia}.zip",
            f"sigtap_{competencia}.zip",
            f"TabelaUnificada_{competencia}.zip",
        ]
        return [f"{base}/{name}" for name in candidates]

    def _download_zip(self, competencia: str) -> bytes:
        if self.fetcher:
            return self.fetcher(competencia)

        errors: List[str] = []
        for url in self._build_urls(competencia):
            try:
                resp = httpx.get(url, timeout=60)
                resp.raise_for_status()
                return resp.content
            except Exception as exc:
                errors.append(f"{url}: {exc}")
        raise RuntimeError(f"Nao foi possivel baixar SIGTAP {competencia}. Tentativas: {' | '.join(errors)}")

    def _parse_zip(self, zip_bytes: bytes, competencia: str) -> List[Dict]:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            proc_name = _find_first_matching(zf, ("proced", "tb_procedimento"))
            if not proc_name:
                raise RuntimeError("Pacote SIGTAP sem tabela de procedimentos")
            regra_name = _find_first_matching(zf, ("regra", "restricao", "condicao"))

            proc_rows = _iter_csv_rows(zf.read(proc_name))
            regra_rows = _iter_csv_rows(zf.read(regra_name)) if regra_name else []
            regra_map = _montar_regra_map(regra_rows)
            return _parse_procedimento_rows(proc_rows, regra_map, competencia)

    def sync(self, competencia: str) -> Dict[str, object]:
        competencia = competencia.strip()
        if len(competencia) != 6 or not competencia.isdigit():
            raise ValueError("Competencia deve estar no formato AAAAMM")

        zip_bytes = self._download_zip(competencia)
        registros = self._parse_zip(zip_bytes, competencia)

        inseridos = 0
        ja_existiam = 0
        for item in registros:
            if self.repository.salvar(item):
                inseridos += 1
            else:
                ja_existiam += 1

        return {
            "competencia": competencia,
            "importados": inseridos,
            "ja_existiam": ja_existiam,
            "total_registros": self.repository.total_registros(),
            "quando": datetime.utcnow().isoformat(),
        }
