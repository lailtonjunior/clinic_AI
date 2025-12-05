import csv
import io
import zipfile
from datetime import date
from types import SimpleNamespace

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.services import sigtap_rules
from app.services.sigtap_sync import SIGTAPSyncService, TabelaSIGTAPRepository


def _csv_content(rows):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()), delimiter=";")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def _build_zip(proc_rows, regra_rows):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("procedimentos.csv", _csv_content(proc_rows))
        if regra_rows:
            zf.writestr("regras.csv", _csv_content(regra_rows))
    return buffer.getvalue()


def _session():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, future=True)()


def test_sigtap_sync_realistic_and_vigencia_lookup():
    proc_202412 = [
        {
            "CO_PROCEDIMENTO": "0301010030",
            "NO_PROCEDIMENTO": "Consulta medica",
            "EXIGE_CID": "N",
            "EXIGE_APAC": "",
            "TP_SEXO": "A",
            "NU_IDADE_MINIMA": "",
            "NU_IDADE_MAXIMA": "",
            "CO_COMPLEXIDADE": "01",
            "CO_MODALIDADE": "01",
            "DT_INICIO": "202412",
            "DT_FIM": "",
            "DOC_PACIENTE": "CNS",
        },
        {
            "CO_PROCEDIMENTO": "1234567890",
            "NO_PROCEDIMENTO": "Procedimento APAC",
            "EXIGE_CID": "",
            "EXIGE_APAC": "",
            "TP_SEXO": "F",
            "NU_IDADE_MINIMA": "18",
            "NU_IDADE_MAXIMA": "35",
            "CO_COMPLEXIDADE": "02",
            "CO_MODALIDADE": "03",
            "DT_INICIO": "202412",
            "DT_FIM": "202412",
            "DOC_PACIENTE": "CPF",
        },
    ]
    regras_202412 = [
        {
            "CO_PROCEDIMENTO": "1234567890",
            "EXIGE_APAC": "S",
            "EXIGE_CID": "S",
            "TP_SEXO": "F",
            "NU_IDADE_MINIMA": "18",
            "NU_IDADE_MAXIMA": "35",
            "DT_INICIO": "202412",
            "DT_FIM": "202412",
            "DOC_PACIENTE": "CPF",
        }
    ]
    proc_202501 = [
        {
            "CO_PROCEDIMENTO": "1234567890",
            "NO_PROCEDIMENTO": "Procedimento APAC",
            "EXIGE_CID": "S",
            "EXIGE_APAC": "S",
            "TP_SEXO": "F",
            "NU_IDADE_MINIMA": "18",
            "NU_IDADE_MAXIMA": "60",
            "CO_COMPLEXIDADE": "02",
            "CO_MODALIDADE": "04",
            "DT_INICIO": "202501",
            "DT_FIM": "",
            "DOC_PACIENTE": "CPF",
        }
    ]

    fixtures = {
        "202412": _build_zip(proc_202412, regras_202412),
        "202501": _build_zip(proc_202501, []),
    }

    session = _session()
    repo = TabelaSIGTAPRepository(session)
    service = SIGTAPSyncService(repo, fetcher=lambda comp: fixtures[comp])

    service.sync("202412")
    service.sync("202501")

    assert repo.competencia_importada("202412")
    assert repo.competencia_importada("202501")
    assert repo.total_registros() == 3  # 2 + 1 sem duplicar vigencia_inicio

    tabela_2024 = sigtap_rules.get_tabela_para_competencia(session, "1234567890", "202412")
    tabela_2025 = sigtap_rules.get_tabela_para_competencia(session, "1234567890", "202503")
    assert tabela_2024 is not None
    assert tabela_2024.vigencia_inicio == "202412"
    assert tabela_2024.exige_apac is True
    assert tabela_2025 is not None
    assert tabela_2025.vigencia_inicio == "202501"
    assert tabela_2025.idade_max == 60

    paciente_f = SimpleNamespace(cns="898001160660001", cpf="12345678901", sexo="F", data_nascimento=date(1990, 1, 1))
    paciente_jovem = SimpleNamespace(cns="898001160660001", cpf="12345678901", sexo="F", data_nascimento=date(2015, 1, 1))
    profissional = SimpleNamespace(cns="898001160660001")
    unidade = SimpleNamespace(cnes="1234560")
    proc_model = SimpleNamespace(
        sigtap_codigo="1234567890",
        cid10="F329",
        quantidade=1,
        profissional_cbo="2231",
        valores={"valor": 100.0},
        competencia_aaaamm="202501",
    )

    erros_validos = sigtap_rules.validate_procedimento(
        session, paciente_f, proc_model, unidade, profissional, date(2025, 1, 10), tabela_proc=tabela_2025
    )
    assert "procedimento_exige_apac" in erros_validos
    assert "procedimento_fora_vigencia" not in erros_validos

    erros_idade = sigtap_rules.validate_procedimento(
        session, paciente_jovem, proc_model, unidade, profissional, date(2025, 1, 10), tabela_proc=tabela_2025
    )
    assert "idade_inferior_limite" in erros_idade

    proc_model_antigo = SimpleNamespace(
        sigtap_codigo="1234567890",
        cid10="F329",
        quantidade=1,
        profissional_cbo="2231",
        valores={"valor": 100.0},
        competencia_aaaamm="202410",
    )
    erros_vigencia = sigtap_rules.validate_procedimento(
        session, paciente_f, proc_model_antigo, unidade, profissional, date(2024, 10, 10)
    )
    assert "procedimento_fora_vigencia" in erros_vigencia
    session.close()
