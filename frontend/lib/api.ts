import { authHeaders, getSession } from "./auth";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export type AuditError = { procedimento_id: number; erros: string[] };
export type AuditResponse = { competencia: string; erros: AuditError[] };

async function handleJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export async function getAudit(competencia: string): Promise<AuditResponse> {
  const session = getSession();
  const res = await fetch(`${API_BASE}/api/audit/competencia/${competencia}`, {
    headers: { ...authHeaders(session) },
  });
  return handleJson<AuditResponse>(res);
}

export async function postBpa(competencia: string): Promise<{ url: string; preview: string }> {
  const session = getSession();
  const res = await fetch(`${API_BASE}/api/exports/bpa?competencia=${competencia}`, {
    method: "POST",
    headers: { ...authHeaders(session) },
  });
  return handleJson(res);
}

export async function postApac(competencia: string): Promise<{ url: string; preview: string }> {
  const session = getSession();
  const res = await fetch(`${API_BASE}/api/exports/apac?competencia=${competencia}`, {
    method: "POST",
    headers: { ...authHeaders(session) },
  });
  return handleJson(res);
}

export async function fetchRemFile(url: string): Promise<string> {
  const res = await fetch(`${API_BASE}/${url.replace(/^\\//, "")}`);
  if (!res.ok) {
    throw new Error(`Falha ao baixar arquivo ${url}`);
  }
  return res.text();
}

export async function getUsers() {
  const session = getSession();
  const res = await fetch(`${API_BASE}/api/users`, { headers: { ...authHeaders(session) } });
  return handleJson(res);
}

export async function createUser(payload: any) {
  const session = getSession();
  const res = await fetch(`${API_BASE}/api/users`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders(session) },
    body: JSON.stringify(payload),
  });
  return handleJson(res);
}

export async function updateUser(id: number, payload: any) {
  const session = getSession();
  const res = await fetch(`${API_BASE}/api/users/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...authHeaders(session) },
    body: JSON.stringify(payload),
  });
  return handleJson(res);
}

export async function resetUserPassword(id: number, payload: any = {}) {
  const session = getSession();
  const res = await fetch(`${API_BASE}/api/users/${id}/reset-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders(session) },
    body: JSON.stringify(payload),
  });
  return handleJson(res);
}

export async function getTenants() {
  const session = getSession();
  const res = await fetch(`${API_BASE}/api/tenants`, { headers: { ...authHeaders(session) } });
  return handleJson(res);
}

export async function createTenant(payload: any) {
  const session = getSession();
  const res = await fetch(`${API_BASE}/api/tenants`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders(session) },
    body: JSON.stringify(payload),
  });
  return handleJson(res);
}

export async function updateTenant(id: number, payload: any) {
  const session = getSession();
  const res = await fetch(`${API_BASE}/api/tenants/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...authHeaders(session) },
    body: JSON.stringify(payload),
  });
  return handleJson(res);
}

export async function changePassword(payload: { senha_atual: string; senha_nova: string }) {
  const session = getSession();
  const res = await fetch(`${API_BASE}/api/auth/change-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders(session) },
    body: JSON.stringify(payload),
  });
  return handleJson(res);
}
