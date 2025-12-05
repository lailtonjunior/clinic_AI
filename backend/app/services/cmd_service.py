from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.services import cmd_client, cmd_mapper


class CmdService:
    def __init__(self, db: Session):
        self.db = db

    def _get_config(self, tenant_id: int) -> models.CmdConfigTenant:
        cfg = self.db.scalars(select(models.CmdConfigTenant).where(models.CmdConfigTenant.tenant_id == tenant_id)).first()
        if not cfg or not cfg.ativo:
            raise RuntimeError("Config CMD inativa ou inexistente")
        return cfg

    def _client_from_cfg(self, cfg: models.CmdConfigTenant) -> cmd_client.CmdSoapClient:
        return cmd_client.CmdSoapClient(
            cfg.wsdl_url,
            cfg.usuario_servico,
            cfg.senha_servico,
            cfg.cpf_operador,
            cfg.senha_operador,
        )

    def criar_ou_atualizar_cmd_para_atendimento(self, tenant_id: int, atendimento_id: int, competencia: str) -> models.CmdContato:
        contato = self.db.scalars(
            select(models.CmdContato).where(
                models.CmdContato.tenant_id == tenant_id,
                models.CmdContato.atendimento_id == atendimento_id,
                models.CmdContato.competencia == competencia,
            )
        ).first()
        if contato:
            return contato
        atendimento = self.db.get(models.Atendimento, atendimento_id)
        paciente = self.db.get(models.Paciente, atendimento.paciente_id)
        unidade = self.db.get(models.Unidade, atendimento.unidade_id)
        procedimentos = self.db.scalars(select(models.ProcedimentoSUS).where(models.ProcedimentoSUS.atendimento_id == atendimento_id)).all()
        dados_cmd = cmd_mapper.mapear_atendimento_para_cmd(atendimento, procedimentos, paciente, unidade, competencia)
        contato = models.CmdContato(
            tenant_id=tenant_id,
            paciente_id=paciente.id,
            unidade_id=unidade.id,
            atendimento_id=atendimento_id,
            competencia=competencia,
            data_admissao=dados_cmd.get("data_admissao"),
            cid_principal=dados_cmd.get("cid_principal"),
            resumo_procedimentos=dados_cmd.get("procedimentos"),
            status_envio_cmd="PENDENTE",
        )
        self.db.add(contato)
        self.db.commit()
        self.db.refresh(contato)
        return contato

    def enviar_contato(self, tenant_id: int, cmd_contato_id: int) -> models.CmdContato:
        contato = self.db.get(models.CmdContato, cmd_contato_id)
        if not contato or contato.tenant_id != tenant_id:
            raise RuntimeError("CmdContato nao encontrado")
        cfg = self._get_config(tenant_id)
        client = self._client_from_cfg(cfg)

        atendimento = self.db.get(models.Atendimento, contato.atendimento_id) if contato.atendimento_id else None
        paciente = self.db.get(models.Paciente, contato.paciente_id)
        unidade = self.db.get(models.Unidade, contato.unidade_id)
        procedimentos = self.db.scalars(select(models.ProcedimentoSUS).where(models.ProcedimentoSUS.atendimento_id == contato.atendimento_id)).all() if contato.atendimento_id else []
        dados_cmd = cmd_mapper.mapear_atendimento_para_cmd(atendimento, procedimentos, paciente, unidade, contato.competencia)
        xml_dados = cmd_mapper.build_dados_contato_xml(dados_cmd)

        if contato.codigo_cmd_uuid:
            status, codigo, mensagem = client.alterar_contato(xml_dados)
        else:
            status, codigo, mensagem = client.incluir_contato(xml_dados)

        contato.data_ultimo_envio_cmd = datetime.utcnow()
        if status == 200 and codigo == "0":
            contato.status_envio_cmd = "ENVIADO"
            # TODO: extrair uuid da resposta real quando especificado
            if not contato.codigo_cmd_uuid:
                contato.codigo_cmd_uuid = contato.codigo_cmd_uuid or "UUID-GERADO-SERVER"
        else:
            contato.status_envio_cmd = "REJEITADO"
            contato.ultimo_erro_cmd = f"{codigo}: {mensagem}"
        self.db.add(contato)
        self.db.commit()
        self.db.refresh(contato)
        return contato

    def cancelar_contato(self, tenant_id: int, cmd_contato_id: int, motivo: str = "Cancelado pelo sistema") -> models.CmdContato:
        contato = self.db.get(models.CmdContato, cmd_contato_id)
        if not contato or contato.tenant_id != tenant_id:
            raise RuntimeError("CmdContato nao encontrado")
        if not contato.codigo_cmd_uuid:
            raise RuntimeError("Contato sem UUID CMD")
        cfg = self._get_config(tenant_id)
        client = self._client_from_cfg(cfg)
        status, codigo, mensagem = client.cancelar_contato(contato.codigo_cmd_uuid, motivo)
        contato.data_ultimo_envio_cmd = datetime.utcnow()
        if status == 200 and codigo == "0":
            contato.status_envio_cmd = "CANCELADO"
        else:
            contato.ultimo_erro_cmd = f"{codigo}: {mensagem}"
        self.db.add(contato)
        self.db.commit()
        self.db.refresh(contato)
        return contato

    def enviar_pendentes_por_competencia(self, tenant_id: int, competencia: str):
        contatos = self.db.scalars(
            select(models.CmdContato).where(
                models.CmdContato.tenant_id == tenant_id,
                models.CmdContato.competencia == competencia,
                models.CmdContato.status_envio_cmd == "PENDENTE",
            )
        ).all()
        results = []
        for c in contatos:
            try:
                results.append(self.enviar_contato(tenant_id, c.id))
            except Exception as exc:
                c.status_envio_cmd = "REJEITADO"
                c.ultimo_erro_cmd = str(exc)
                self.db.add(c)
                self.db.commit()
                results.append(c)
        return results
