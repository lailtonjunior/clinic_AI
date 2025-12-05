from datetime import datetime, date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app import models
from app.services.cmd_service import CmdService
from app.services import cmd_client


class DummyCmdClient(cmd_client.CmdSoapClient):
    def __init__(self):
        super().__init__("http://test", "u", "p", "cpf", "s")

    def incluir_contato(self, dados_xml):
        return 200, "0", "ok"

    def alterar_contato(self, dados_xml):
        return 200, "0", "ok"

    def cancelar_contato(self, uuid_cmd: str, motivo: str):
        return 200, "0", "ok"


def _session():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, future=True)()


def seed_basic(db):
    tenant = models.Tenant(name="Tenant", cnpj="123")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    unidade = models.Unidade(
        tenant_id=tenant.id,
        nome="Unid",
        cnes="1234567",
        cnpj="12345678000199",
        uf="DF",
        ibge_cod="5300108",
        destino="M",
        competencia_params={},
    )
    db.add(unidade)
    paciente = models.Paciente(
        tenant_id=tenant.id,
        nome="Paciente",
        cpf="12345678901",
        cns="898001160660001",
        nome_social=None,
        nome_mae="Mae",
        sexo="M",
        data_nascimento=date(1990, 1, 1),
        ibge_cod="5300108",
        contato={},
        pcd=False,
        cid_deficiencia=None,
    )
    db.add(paciente)
    atendimento = models.Atendimento(
        tenant_id=tenant.id,
        unidade_id=1,
        profissional_id=1,
        paciente_id=1,
        tipo="consulta",
        data=datetime(2025, 1, 1, 10, 0),
        status="concluido",
    )
    db.add(atendimento)
    proc = models.ProcedimentoSUS(
        tenant_id=tenant.id,
        atendimento_id=1,
        sigtap_codigo="0301010030",
        cid10="F329",
        quantidade=1,
        profissional_cbo="225120",
        valores={"valor": 10.0},
        competencia_aaaamm="202501",
        validacoes_json={},
    )
    db.add(proc)
    cfg = models.CmdConfigTenant(
        tenant_id=tenant.id,
        cnes_estabelecimento="1234567",
        wsdl_url="http://test",
        usuario_servico="u",
        senha_servico="p",
        cpf_operador="12345678901",
        senha_operador="s",
        ambiente="HOMOLOG",
        ativo=True,
    )
    db.add(cfg)
    db.commit()
    return tenant


def test_cmd_service_creates_and_sends(monkeypatch):
    db = _session()
    tenant = seed_basic(db)
    service = CmdService(db)

    # monkeypatch client creation
    def fake_client(cfg):
        return DummyCmdClient()

    monkeypatch.setattr(service, "_client_from_cfg", fake_client)

    contato = service.criar_ou_atualizar_cmd_para_atendimento(tenant.id, 1, "202501")
    assert contato.status_envio_cmd == "PENDENTE"
    contato = service.enviar_contato(tenant.id, contato.id)
    assert contato.status_envio_cmd in {"ENVIADO", "REJEITADO"}
    if contato.codigo_cmd_uuid:
        contato = service.cancelar_contato(tenant.id, contato.id, motivo="Teste")
        assert contato.status_envio_cmd in {"CANCELADO", "REJEITADO"}
