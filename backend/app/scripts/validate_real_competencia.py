import argparse
import json
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, List

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app import models
from app.services import sigtap_rules, export_bpa, export_apac


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _reset_competencia(db: Session, competencia: str):
    db.execute(delete(models.ProcedimentoSUS).where(models.ProcedimentoSUS.competencia_aaaamm == competencia))
    db.execute(delete(models.CompetenciaAberta).where(models.CompetenciaAberta.competencia == competencia))
    db.commit()


def _get_or_create(db: Session, model, defaults: Dict[str, Any], **kwargs):
    instance = db.scalars(select(model).filter_by(**kwargs)).first()
    if instance:
        return instance
    params = dict(defaults)
    params.update(kwargs)
    instance = model(**params)
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


def _seed_from_fixture(db: Session, payload: Dict[str, Any], competencia: str):
    tenant_data = payload.get("tenant") or {"name": "Tenant Fixture", "cnpj": "00000000000000"}
    tenant = _get_or_create(db, models.Tenant, tenant_data, id=tenant_data.get("id", 1))

    for unidade in payload.get("unidades", []):
        _get_or_create(db, models.Unidade, unidade, id=unidade["id"])
        _get_or_create(
            db,
            models.CompetenciaAberta,
            {
                "unidade_cnes": unidade["cnes"],
                "competencia": competencia,
                "aberta": True,
                "data_abertura": date.today(),
            },
            unidade_cnes=unidade["cnes"],
            competencia=competencia,
        )

    for prof in payload.get("profissionais", []):
        _get_or_create(db, models.Profissional, prof, id=prof["id"])

    for pac in payload.get("pacientes", []):
        _get_or_create(db, models.Paciente, pac, id=pac["id"])

    for atendimento in payload.get("atendimentos", []):
        at_data = dict(atendimento)
        if isinstance(at_data.get("data"), str):
            at_data["data"] = datetime.fromisoformat(at_data["data"])
        _get_or_create(db, models.Atendimento, at_data, id=atendimento["id"])

    for tab in payload.get("tabelas_sigtap", []):
        _get_or_create(db, models.TabelaSIGTAP, tab, codigo=tab["codigo"])

    for proc in payload.get("procedimentos", []):
        _get_or_create(db, models.ProcedimentoSUS, proc, id=proc["id"])


def _build_bpa_payloads(db: Session, competencia: str) -> List[Dict[str, Any]]:
    procedimentos = db.scalars(select(models.ProcedimentoSUS).where(models.ProcedimentoSUS.competencia_aaaamm == competencia)).all()
    linhas = []
    for proc in procedimentos:
        atendimento = db.get(models.Atendimento, proc.atendimento_id)
        paciente = db.get(models.Paciente, atendimento.paciente_id)
        profissional = db.get(models.Profissional, atendimento.profissional_id)
        unidade = db.get(models.Unidade, atendimento.unidade_id)
        tabela = sigtap_rules.get_tabela_para_competencia(db, proc.sigtap_codigo, proc.competencia_aaaamm)
        doc = sigtap_rules.decide_documento_bpa(paciente, tabela)
        linhas.append({
            "cnes": unidade.cnes,
            "competencia": proc.competencia_aaaamm,
            "cns_prof": profissional.cns,
            "cbo": proc.profissional_cbo,
            "data_atendimento": atendimento.data.strftime("%Y%m%d"),
            "procedimento": proc.sigtap_codigo,
            "cns_paciente": paciente.cns if doc == "CNS" else "",
            "cpf_paciente": paciente.cpf if doc == "CPF" else "",
            "sexo": paciente.sexo,
            "cid": proc.cid10,
            "idade": sigtap_rules.calcular_idade(paciente.data_nascimento, atendimento.data.date()),
            "quantidade": proc.quantidade,
            "valor": proc.valores.get("valor", 0) if proc.valores else 0,
        })
    return linhas


def _build_apac_payload(db: Session, competencia: str):
    procedimentos = db.scalars(select(models.ProcedimentoSUS).where(models.ProcedimentoSUS.competencia_aaaamm == competencia)).all()
    procedimentos_apac = []
    for proc in procedimentos:
        tabela = sigtap_rules.get_tabela_para_competencia(db, proc.sigtap_codigo, proc.competencia_aaaamm)
        if tabela and tabela.exige_apac:
            procedimentos_apac.append(proc)
    if not procedimentos_apac:
        return None, []
    proc = procedimentos_apac[0]
    atendimento = db.get(models.Atendimento, proc.atendimento_id)
    paciente = db.get(models.Paciente, atendimento.paciente_id)
    profissional = db.get(models.Profissional, atendimento.profissional_id)
    unidade = db.get(models.Unidade, atendimento.unidade_id)
    corpo = {
        "competencia": competencia,
        "numero_apac": "0000000000001",
        "uf": unidade.uf,
        "cnes": unidade.cnes,
        "data_autorizacao": atendimento.data.strftime("%Y%m%d"),
        "data_validade": atendimento.data.strftime("%Y%m%d"),
        "tipo_atendimento": "01",
        "tipo_apac": "1",
        "cns_paciente": paciente.cns,
        "nome_paciente": paciente.nome,
        "nome_mae": paciente.nome_mae or "",
        "logradouro": (paciente.contato or {}).get("logradouro", "logradouro"),
        "numero_endereco": str((paciente.contato or {}).get("numero", "0")),
        "complemento": (paciente.contato or {}).get("complemento", ""),
        "cep": str((paciente.contato or {}).get("cep", "0")),
        "municipio_ibge": unidade.ibge_cod,
        "data_nascimento": paciente.data_nascimento.strftime("%Y%m%d"),
        "sexo": paciente.sexo,
        "nome_medico_responsavel": profissional.nome,
        "procedimento_principal": proc.sigtap_codigo,
        "motivo_saida": "01",
        "data_obito_alta": "",
        "nome_autorizador": profissional.nome,
        "cns_medico_resp": profissional.cns,
        "cns_autorizador": profissional.cns,
        "cid_associado": proc.cid10,
        "num_prontuario": str(atendimento.id).zfill(10),
        "cnes_solicitante": unidade.cnes,
        "data_solicitacao": atendimento.data.strftime("%Y%m%d"),
        "codigo_emissor": proc.sigtap_codigo,
        "carater_atendimento": "01",
        "apac_anterior": "",
        "raca_cor": (paciente.contato or {}).get("raca_cor", "99"),
        "nome_responsavel": paciente.nome_mae or paciente.nome,
        "nacionalidade": (paciente.contato or {}).get("nacionalidade", "010"),
        "etnia": (paciente.contato or {}).get("etnia", "") if (paciente.contato or {}).get("raca_cor") == "05" else "",
        "cod_logradouro_ibge": (paciente.contato or {}).get("tipo_logradouro", "001"),
        "bairro": (paciente.contato or {}).get("bairro", "bairro"),
        "ddd": (paciente.contato or {}).get("ddd", ""),
        "fone": (paciente.contato or {}).get("fone", ""),
        "email": (paciente.contato or {}).get("email", ""),
        "cns_executor": profissional.cns,
        "cpf_paciente": paciente.cpf or "",
        "ine": unidade.ibge_cod,
        "pessoa_rua": (paciente.contato or {}).get("pessoa_rua", ""),
        "fonte_orc": "",
        "emenda": "",
        "fim": "  ",
        "data_processamento": atendimento.data.strftime("%Y%m%d"),
        "data_inicio_validade": atendimento.data.strftime("%Y%m%d"),
        "data_fim_validade": atendimento.data.strftime("%Y%m%d"),
        "tipo_atendimento": "01",
        "tipo_apac": "1",
    }
    procs = []
    for proc in procedimentos_apac:
        procs.append({
            "competencia": competencia,
            "numero_apac": corpo["numero_apac"],
            "codigo": proc.sigtap_codigo,
            "quantidade": proc.quantidade,
            "cbo": proc.profissional_cbo,
        })
    return corpo, procs


def _write_text(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _diff_lines(generated: List[str], reference: List[str]) -> List[str]:
    diffs = []
    max_len = max(len(generated), len(reference))
    for idx in range(max_len):
        got = generated[idx].rstrip("\n") if idx < len(generated) else ""
        ref = reference[idx].rstrip("\n") if idx < len(reference) else ""
        if got != ref:
            diffs.append(f"- Linha {idx+1}: esperado='{ref}' | obtido='{got}'")
    return diffs


def main():
    parser = argparse.ArgumentParser(description="Validacao real de competencia com fixtures anonimizadas.")
    parser.add_argument("competencia", help="AAAAMM da competencia")
    parser.add_argument("--fixture", default="app/tests/fixtures/real_competencia/sample_202501.json", help="Caminho do JSON de fixture")
    parser.add_argument("--ref-bpa", type=str, help="Arquivo BPA de referencia aceito no MAG")
    parser.add_argument("--ref-apac", type=str, help="Arquivo APAC de referencia aceito no MAG")
    args = parser.parse_args()

    competencia = args.competencia
    fixture_path = Path(args.fixture)
    data = _load_json(fixture_path)

    session = SessionLocal()
    try:
        _reset_competencia(session, competencia)
        _seed_from_fixture(session, data, competencia)

        linhas_bpa = _build_bpa_payloads(session, competencia)
        conteudo_bpa = export_bpa.gerar_arquivo(
            competencia=competencia,
            orgao="CER",
            sigla="CER",
            cnpj="00000000000000",
            destino="M",
            versao="0.1.0",
            procedimentos=linhas_bpa,
        )
        bpa_path = Path("app/tests/output") / f"bpa_{competencia}.rem"
        _write_text(bpa_path, conteudo_bpa)

        corpo_apac, procs_apac = _build_apac_payload(session, competencia)
        conteudo_apac = ""
        if corpo_apac:
            conteudo_apac = export_apac.gerar_arquivo(
                competencia=competencia,
                orgao="CER",
                sigla="CER",
                cnpj="00000000000000",
                destino="SES",
                versao="0.1.0",
                corpo=corpo_apac,
                procedimentos=procs_apac,
            )
            apac_path = Path("app/tests/output") / f"apac_{competencia}.rem"
            _write_text(apac_path, conteudo_apac)

        relatorio_lines = []
        if args.ref_bpa:
            ref_bpa_lines = Path(args.ref_bpa).read_text(encoding="utf-8").splitlines()
            diffs_bpa = _diff_lines(conteudo_bpa.splitlines(), ref_bpa_lines)
            if diffs_bpa:
                relatorio_lines.append("## Divergencias BPA")
                relatorio_lines.extend(diffs_bpa)
        if args.ref_apac and conteudo_apac:
            ref_apac_lines = Path(args.ref_apac).read_text(encoding="utf-8").splitlines()
            diffs_apac = _diff_lines(conteudo_apac.splitlines(), ref_apac_lines)
            if diffs_apac:
                relatorio_lines.append("## Divergencias APAC")
                relatorio_lines.extend(diffs_apac)
        if relatorio_lines:
            rel_path = Path("app/tests/output") / f"relatorio_diff_{competencia}.md"
            _write_text(rel_path, "\n".join(relatorio_lines))
            print(f"Relatorio de divergencias salvo em {rel_path}")
        else:
            print("Sem divergencias criticas.")
    finally:
        session.close()


if __name__ == "__main__":
    main()

