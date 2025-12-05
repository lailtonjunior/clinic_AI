import json
from datetime import datetime, date
from pathlib import Path

from app.services import export_bpa, export_apac, sigtap_rules


FIXTURE_PATH = Path("app/tests/fixtures/real_competencia/sample_202501.json")


def _load_fixture():
    with FIXTURE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _calc_age(birth: str, at_date: str) -> int:
    d_birth = date.fromisoformat(birth)
    d_at = datetime.fromisoformat(at_date).date()
    return sigtap_rules.calcular_idade(d_birth, d_at)


def test_real_snapshot_bpa_apac():
    fx = _load_fixture()
    competencia = fx["competencia"]
    unidades = {u["id"]: u for u in fx["unidades"]}
    profissionais = {p["id"]: p for p in fx["profissionais"]}
    pacientes = {p["id"]: p for p in fx["pacientes"]}
    atendimentos = {a["id"]: a for a in fx["atendimentos"]}
    tabelas = {t["codigo"]: t for t in fx["tabelas_sigtap"]}

    bpa_payloads = []
    apac_procs = []
    apac_body = None

    for proc in fx["procedimentos"]:
        at = atendimentos[proc["atendimento_id"]]
        pac = pacientes[at["paciente_id"]]
        prof = profissionais[at["profissional_id"]]
        unid = unidades[at["unidade_id"]]
        tabela = tabelas.get(proc["sigtap_codigo"], {})
        doc_rule = tabela.get("doc_paciente", "CNS")
        doc_is_cns = doc_rule == "CNS"
        bpa_payloads.append({
            "cnes": unid["cnes"],
            "competencia": competencia,
            "cns_prof": prof["cns"],
            "cbo": proc["profissional_cbo"],
            "data_atendimento": datetime.fromisoformat(at["data"]).strftime("%Y%m%d"),
            "procedimento": proc["sigtap_codigo"],
            "cns_paciente": pac["cns"] if doc_is_cns else "",
            "cpf_paciente": pac["cpf"] if not doc_is_cns else "",
            "sexo": pac["sexo"],
            "cid": proc["cid10"],
            "idade": _calc_age(pac["data_nascimento"], at["data"]),
            "quantidade": proc["quantidade"],
            "valor": proc.get("valores", {}).get("valor", 0),
        })
        if tabela.get("exige_apac"):
            apac_body = {
                "competencia": competencia,
                "numero_apac": "0000000000001",
                "uf": unid["uf"],
                "cnes": unid["cnes"],
                "data_autorizacao": datetime.fromisoformat(at["data"]).strftime("%Y%m%d"),
                "data_validade": datetime.fromisoformat(at["data"]).strftime("%Y%m%d"),
                "tipo_atendimento": "01",
                "tipo_apac": "1",
                "cns_paciente": pac["cns"],
                "nome_paciente": pac["nome"],
                "nome_mae": pac["nome_mae"] or "",
                "logradouro": (pac.get("contato") or {}).get("logradouro", "logradouro"),
                "numero_endereco": str((pac.get("contato") or {}).get("numero", "0")),
                "complemento": (pac.get("contato") or {}).get("complemento", ""),
                "cep": str((pac.get("contato") or {}).get("cep", "0")),
                "municipio_ibge": unid["ibge_cod"],
                "data_nascimento": date.fromisoformat(pac["data_nascimento"]).strftime("%Y%m%d"),
                "sexo": pac["sexo"],
                "nome_medico_responsavel": prof["nome"],
                "procedimento_principal": proc["sigtap_codigo"],
                "motivo_saida": "01",
                "data_obito_alta": "",
                "nome_autorizador": prof["nome"],
                "cns_medico_resp": prof["cns"],
                "cns_autorizador": prof["cns"],
                "cid_associado": proc["cid10"],
                "num_prontuario": str(at["id"]).zfill(10),
                "cnes_solicitante": unid["cnes"],
                "data_solicitacao": datetime.fromisoformat(at["data"]).strftime("%Y%m%d"),
                "codigo_emissor": proc["sigtap_codigo"],
                "carater_atendimento": "01",
                "apac_anterior": "",
                "raca_cor": (pac.get("contato") or {}).get("raca_cor", "99"),
                "nome_responsavel": pac["nome_mae"] or pac["nome"],
                "nacionalidade": (pac.get("contato") or {}).get("nacionalidade", "010"),
                "etnia": (pac.get("contato") or {}).get("etnia", "") if (pac.get("contato") or {}).get("raca_cor") == "05" else "",
                "cod_logradouro_ibge": (pac.get("contato") or {}).get("tipo_logradouro", "001"),
                "bairro": (pac.get("contato") or {}).get("bairro", "bairro"),
                "ddd": (pac.get("contato") or {}).get("ddd", ""),
                "fone": (pac.get("contato") or {}).get("fone", ""),
                "email": (pac.get("contato") or {}).get("email", ""),
                "cns_executor": prof["cns"],
                "cpf_paciente": pac["cpf"] or "",
                "ine": unid["ibge_cod"],
                "pessoa_rua": (pac.get("contato") or {}).get("pessoa_rua", ""),
                "fonte_orc": "",
                "emenda": "",
                "fim": "  ",
                "data_processamento": datetime.fromisoformat(at["data"]).strftime("%Y%m%d"),
                "data_inicio_validade": datetime.fromisoformat(at["data"]).strftime("%Y%m%d"),
                "data_fim_validade": datetime.fromisoformat(at["data"]).strftime("%Y%m%d"),
                "tipo_atendimento": "01",
                "tipo_apac": "1",
            }
            apac_procs.append({
                "competencia": competencia,
                "numero_apac": "0000000000001",
                "codigo": proc["sigtap_codigo"],
                "quantidade": proc["quantidade"],
                "cbo": proc["profissional_cbo"],
            })

    conteudo_bpa = export_bpa.gerar_arquivo(
        competencia=competencia,
        orgao="CER",
        sigla="CER",
        cnpj="00000000000000",
        destino="M",
        versao="0.1.0",
        procedimentos=bpa_payloads,
    )
    linhas_bpa = conteudo_bpa.splitlines(keepends=True)
    header_bpa = linhas_bpa[0]
    header_body = header_bpa.rstrip("\r\n")
    assert header_bpa.endswith("\r\n")
    assert header_body[0:2] == "01"
    assert header_body[2:7] == "#BPA#"
    assert len(header_body) == export_bpa.HEADER_LEN
    assert linhas_bpa[-1].startswith("99#BPA")
    assert len(linhas_bpa) == len(bpa_payloads) + 2

    if apac_body:
        conteudo_apac = export_apac.gerar_arquivo(
            competencia=competencia,
            orgao="CER",
            sigla="CER",
            cnpj="00000000000000",
            destino="SES",
            versao="0.1.0",
            corpo=apac_body,
            procedimentos=apac_procs,
        )
        linhas_apac = conteudo_apac.splitlines()
        assert linhas_apac[0].startswith("01")
        assert linhas_apac[1].startswith("14")
        assert linhas_apac[2].startswith("13")
        # CRLF garantido: len via rstrip
        assert len(linhas_apac[0]) == export_apac.HEADER_LEN
        assert len(linhas_apac[1]) == export_apac.CORPO_LEN
        assert len(linhas_apac[2]) == export_apac.PROC_LEN
