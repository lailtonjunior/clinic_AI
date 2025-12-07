from datetime import datetime, date
from enum import Enum
from sqlalchemy import Column, String, Integer, Date, DateTime, Boolean, ForeignKey, Text, JSON, Numeric, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.database import Base


class Role(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN_TENANT = "ADMIN_TENANT"
    FATURAMENTO = "FATURAMENTO"
    CLINICO = "CLINICO"
    RECEPCAO = "RECEPCAO"
    AUDITOR_INTERNO = "AUDITOR_INTERNO"


class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    cnpj = Column(String(14), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Unidade(Base):
    __tablename__ = "unidades"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    nome = Column(String(255), nullable=False)
    cnes = Column(String(7), nullable=False, index=True)
    cnpj = Column(String(14), nullable=False)
    uf = Column(String(2), nullable=False)
    ibge_cod = Column(String(7), nullable=False)
    destino = Column(String(1), nullable=False, default="M")
    competencia_params = Column(JSON, default={})


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    nome = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(64), nullable=True)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    must_change_password = Column(Boolean, default=False)


class TenantUserRole(Base):
    __tablename__ = "tenant_user_roles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    role = Column(String(50), nullable=False)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("user_id", "tenant_id", "role", name="uq_user_tenant_role"),)


class Profissional(Base):
    __tablename__ = "profissionais"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    nome = Column(String(255), nullable=False)
    cpf = Column(String(11), nullable=False)
    cns = Column(String(15), nullable=False)
    cbo = Column(String(6), nullable=False)
    conselho = Column(String(50), nullable=True)
    certificado_publico = Column(Text, nullable=True)


class Paciente(Base):
    __tablename__ = "pacientes"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    nome = Column(String(255), nullable=False)
    cpf = Column(String(11), nullable=True)
    cns = Column(String(15), nullable=True)
    nome_social = Column(String(255), nullable=True)
    nome_mae = Column(String(255), nullable=True)
    sexo = Column(String(1), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    ibge_cod = Column(String(7), nullable=False)
    contato = Column(JSON, default={})
    pcd = Column(Boolean, default=False)
    cid_deficiencia = Column(String(10), nullable=True)


class Agenda(Base):
    __tablename__ = "agendas"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    profissional_id = Column(Integer, ForeignKey("profissionais.id"), nullable=False)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=True)
    data = Column(DateTime, nullable=False)
    tipo = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="livre")


class Atendimento(Base):
    __tablename__ = "atendimentos"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    profissional_id = Column(Integer, ForeignKey("profissionais.id"), nullable=False)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    tipo = Column(String(50), nullable=False)
    data = Column(DateTime, nullable=False)
    status = Column(String(50), nullable=False, default="em_andamento")


class EvolucaoProntuario(Base):
    __tablename__ = "evolucoes_prontuario"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    atendimento_id = Column(Integer, ForeignKey("atendimentos.id"), nullable=False)
    texto_estruturado = Column(Text, nullable=False)
    hash_sha256 = Column(String(64), nullable=False)
    assinado = Column(Boolean, default=False)
    assinatura_meta = Column(JSON, default={})
    assinatura_modo = Column(String(20), nullable=False, default="NONE")
    assinatura_hash = Column(String(128), nullable=True)
    assinatura_metadata = Column(JSON, default={})
    criado_em = Column(DateTime, default=datetime.utcnow)


class AnexoClinico(Base):
    __tablename__ = "anexos_clinicos"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    atendimento_id = Column(Integer, ForeignKey("atendimentos.id"), nullable=False)
    tipo = Column(String(50), nullable=False)
    url = Column(String(255), nullable=False)
    hash = Column(String(64), nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)


class ProcedimentoSUS(Base):
    __tablename__ = "procedimentos_sus"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    atendimento_id = Column(Integer, ForeignKey("atendimentos.id"), nullable=False)
    sigtap_codigo = Column(String(10), nullable=False)
    cid10 = Column(String(10), nullable=False)
    quantidade = Column(Integer, nullable=False)
    profissional_cbo = Column(String(6), nullable=False)
    valores = Column(JSON, default={})
    competencia_aaaamm = Column(String(6), nullable=False)
    validacoes_json = Column(JSON, default={})


class ExportacaoBPA(Base):
    __tablename__ = "exportacoes_bpa"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    competencia = Column(String(6), nullable=False)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    arquivo_path = Column(String(255), nullable=True)
    checksum = Column(String(10), nullable=True)
    status = Column(String(50), nullable=False, default="gerado")
    erros_json = Column(JSON, default={})


class ExportacaoAPAC(Base):
    __tablename__ = "exportacoes_apac"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    competencia = Column(String(6), nullable=False)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    arquivo_path = Column(String(255), nullable=True)
    checksum = Column(String(10), nullable=True)
    status = Column(String(50), nullable=False, default="gerado")
    erros_json = Column(JSON, default={})


class CompetenciaAberta(Base):
    __tablename__ = "competencias_abertas"
    id = Column(Integer, primary_key=True)
    unidade_cnes = Column(String(7), nullable=False, index=True)
    competencia = Column(String(6), nullable=False)
    aberta = Column(Boolean, default=True)
    data_abertura = Column(Date, nullable=True)
    data_fechamento_previsto = Column(Date, nullable=True)
    dias_para_lancamento = Column(Integer, default=30)
    cidade = Column(String(100), nullable=True)
    uf = Column(String(2), nullable=True)


class TabelaSIGTAP(Base):
    __tablename__ = "tabelas_sigtap"
    id = Column(Integer, primary_key=True)
    codigo = Column(String(10), nullable=False)
    descricao = Column(String(255), nullable=False)
    valor = Column(Numeric(10,2), nullable=True)
    regras = Column(JSON, default={})
    vigencia = Column(String(6), nullable=False)
    exige_cid = Column(Boolean, default=False)
    exige_apac = Column(Boolean, default=False)
    doc_paciente = Column(String(20), nullable=False, default="AMBOS_PERMITIDOS")
    sexo_permitido = Column(String(1), nullable=False, default="A")  # M/F/A
    idade_min = Column(Integer, nullable=True)
    idade_max = Column(Integer, nullable=True)
    vigencia_inicio = Column(String(6), nullable=True)
    vigencia_fim = Column(String(6), nullable=True)


class TabelaAuxiliar(Base):
    __tablename__ = "tabelas_auxiliares"
    id = Column(Integer, primary_key=True)
    tipo = Column(String(50), nullable=False)
    codigo = Column(String(20), nullable=False)
    descricao = Column(String(255), nullable=False)
    meta_json = Column(JSON, default={})


class CmdContato(Base):
    __tablename__ = "cmd_contatos"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    atendimento_id = Column(Integer, ForeignKey("atendimentos.id"), nullable=True)
    codigo_cmd_uuid = Column(String(36), nullable=True, index=True)
    competencia = Column(String(6), nullable=False, index=True)
    data_admissao = Column(Date, nullable=False)
    data_desfecho = Column(Date, nullable=True)
    modalidade_assistencial = Column(String(10), nullable=True)
    tipo_atendimento = Column(String(10), nullable=True)
    cid_principal = Column(String(10), nullable=True)
    cids_associados = Column(JSON, default=[])
    resumo_procedimentos = Column(JSON, default=[])
    status_envio_cmd = Column(String(20), nullable=False, default="PENDENTE")
    ultimo_erro_cmd = Column(Text, nullable=True)
    data_ultimo_envio_cmd = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (
        Index("idx_cmdcontato_tenant_competencia", "tenant_id", "competencia"),
    )


class CmdConfigTenant(Base):
    __tablename__ = "cmd_config_tenant"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, unique=True)
    cnes_estabelecimento = Column(String(7), nullable=False)
    wsdl_url = Column(String(255), nullable=False)
    usuario_servico = Column(String(100), nullable=False)
    senha_servico = Column(String(200), nullable=False)
    cpf_operador = Column(String(11), nullable=False)
    senha_operador = Column(String(200), nullable=False)
    ambiente = Column(String(20), nullable=False, default="HOMOLOG")
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    acao = Column(String(100), nullable=False)
    entidade = Column(String(100), nullable=False)
    entidade_id = Column(String(50), nullable=True)
    meta_json = Column(JSON, default={})
    criado_em = Column(DateTime, default=datetime.utcnow, index=True)
