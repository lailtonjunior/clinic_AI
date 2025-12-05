from datetime import datetime
from typing import Dict, Any, List
from xml.etree import ElementTree as ET

from app import models


def _text(el: ET.Element, tag: str, value: str):
    node = ET.SubElement(el, tag)
    node.text = value
    return node


def mapear_atendimento_para_cmd(
    atendimento: models.Atendimento,
    procedimentos: List[models.ProcedimentoSUS],
    paciente: models.Paciente,
    unidade: models.Unidade,
    competencia: str,
) -> Dict[str, Any]:
    # Mapeamento mínimo; TODO: completar campos conforme documentação CMD
    return {
        "competencia": competencia,
        "data_admissao": atendimento.data.date() if hasattr(atendimento, "data") else None,
        "modalidade_assistencial": getattr(atendimento, "tipo", None) or "AMBULATORIAL",
        "cnes": unidade.cnes,
        "paciente": {
            "cns": paciente.cns,
            "nome": paciente.nome,
            "sexo": paciente.sexo,
            "data_nascimento": paciente.data_nascimento,
            "cpf": paciente.cpf,
        },
        "cid_principal": procedimentos[0].cid10 if procedimentos else None,
        "procedimentos": [
            {
                "codigo": p.sigtap_codigo,
                "quantidade": p.quantidade,
                "cid": p.cid10,
                "cbo": p.profissional_cbo,
            }
            for p in procedimentos
        ],
    }


def build_dados_contato_xml(dados_cmd: Dict[str, Any]) -> ET.Element:
    req = ET.Element("RequestIncluirContatoAssistencial")
    _text(req, "competencia", dados_cmd.get("competencia", ""))
    _text(req, "dataAdmissao", dados_cmd.get("data_admissao").strftime("%Y-%m-%d") if dados_cmd.get("data_admissao") else "")
    _text(req, "modalidadeAssistencial", dados_cmd.get("modalidade_assistencial", "AMBULATORIAL"))
    ind = ET.SubElement(req, "individuo")
    pac = dados_cmd.get("paciente", {})
    _text(ind, "cns", pac.get("cns", ""))
    _text(ind, "nome", pac.get("nome", ""))
    _text(ind, "sexo", pac.get("sexo", ""))
    if pac.get("data_nascimento"):
        _text(ind, "dataNascimento", pac["data_nascimento"].strftime("%Y-%m-%d"))
    if pac.get("cpf"):
        _text(ind, "cpf", pac["cpf"])
    _text(req, "cidPrincipal", dados_cmd.get("cid_principal") or "")
    procedimentos = dados_cmd.get("procedimentos") or []
    procs_el = ET.SubElement(req, "procedimentos")
    for p in procedimentos:
        pe = ET.SubElement(procs_el, "procedimento")
        _text(pe, "codigoProcedimento", p.get("codigo", ""))
        _text(pe, "quantidade", str(p.get("quantidade", 1)))
        if p.get("cid"):
            _text(pe, "cid", p["cid"])
        if p.get("cbo"):
            _text(pe, "cbo", p["cbo"])
    return req
