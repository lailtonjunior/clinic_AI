from datetime import datetime, date
from typing import Optional, Any
from pydantic import BaseModel


class TenantBase(BaseModel):
    name: str
    cnpj: Optional[str] = None


class TenantCreate(TenantBase):
    pass


class Tenant(TenantBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UnidadeBase(BaseModel):
    tenant_id: int
    nome: str
    cnes: str
    cnpj: str
    uf: str
    ibge_cod: str
    destino: str
    competencia_params: Any | None = None


class UnidadeCreate(UnidadeBase):
    pass


class Unidade(UnidadeBase):
    id: int

    class Config:
        from_attributes = True


class PacienteBase(BaseModel):
    tenant_id: int
    nome: str
    cpf: str | None = None
    cns: str | None = None
    nome_social: str | None = None
    nome_mae: str | None = None
    sexo: str
    data_nascimento: date
    ibge_cod: str
    contato: Any | None = None
    pcd: bool = False
    cid_deficiencia: str | None = None


class PacienteCreate(PacienteBase):
    pass


class Paciente(PacienteBase):
    id: int

    class Config:
        from_attributes = True


class ProfissionalBase(BaseModel):
    tenant_id: int
    unidade_id: int
    nome: str
    cpf: str
    cns: str
    cbo: str
    conselho: str | None = None
    certificado_publico: str | None = None


class ProfissionalCreate(ProfissionalBase):
    pass


class Profissional(ProfissionalBase):
    id: int

    class Config:
        from_attributes = True


class AgendaBase(BaseModel):
    tenant_id: int
    unidade_id: int
    profissional_id: int
    paciente_id: int | None = None
    data: datetime
    tipo: str
    status: str


class AgendaCreate(AgendaBase):
    pass


class Agenda(AgendaBase):
    id: int

    class Config:
        from_attributes = True


class AtendimentoBase(BaseModel):
    tenant_id: int
    unidade_id: int
    profissional_id: int
    paciente_id: int
    tipo: str
    data: datetime
    status: str


class AtendimentoCreate(AtendimentoBase):
    pass


class Atendimento(AtendimentoBase):
    id: int

    class Config:
        from_attributes = True


class EvolucaoBase(BaseModel):
    tenant_id: int
    atendimento_id: int
    texto_estruturado: str
    hash_sha256: str
    assinado: bool
    assinatura_meta: Any | None = None


class EvolucaoCreate(EvolucaoBase):
    pass


class Evolucao(EvolucaoBase):
    id: int
    criado_em: datetime

    class Config:
        from_attributes = True


class ProcedimentoBase(BaseModel):
    tenant_id: int
    atendimento_id: int
    sigtap_codigo: str
    cid10: str
    quantidade: int
    profissional_cbo: str
    valores: Any | None = None
    competencia_aaaamm: str
    validacoes_json: Any | None = None


class ProcedimentoCreate(ProcedimentoBase):
    pass


class Procedimento(ProcedimentoBase):
    id: int

    class Config:
        from_attributes = True
