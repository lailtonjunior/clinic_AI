export type AuditError = { procedimento_id: number; erros: string[] };
export type AuditResponse = { competencia: string; erros: AuditError[] };

export type DashboardResponse = {
  competencia: string;
  total_atendimentos: number;
  total_pacientes: number;
  total_procedimentos: number;
  total_procedimentos_com_erro: number;
  ultimas_exportacoes: {
    id: number;
    tipo: string;
    competencia: string;
    status: string;
    data: string | null;
    erros: unknown;
  }[];
};

export type Tenant = {
  id: number;
  name: string;
  cnpj?: string | null;
};

export type AgendaItem = {
  id: number;
  data: string;
  tipo?: string;
  status?: string;
  profissional_id?: number;
  paciente_id?: number;
  [key: string]: unknown;
};

export type User = {
  id: number;
  email: string;
  nome: string;
  roles: string[];
  ativo: boolean;
  must_change_password: boolean;
};

export type ExportItem = {
  id: number;
  competencia: string;
  status: string;
  arquivo_path?: string;
  erros_json?: Record<string, unknown>;
  tipo?: string;
};

export type Atendimento = {
  id: number;
  paciente_id?: number;
  profissional_id?: number;
  unidade_id?: number;
  data: string;
  tipo?: string;
  status?: string;
  [key: string]: unknown;
};

export type Evolucao = {
  id: number;
  atendimento_id: number;
  texto_estruturado?: string;
  criado_em?: string;
  [key: string]: unknown;
};

export type AssistantReply = {
  resposta: string;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
  tenant_id: number;
  roles: string[];
  must_change_password: boolean;
};
