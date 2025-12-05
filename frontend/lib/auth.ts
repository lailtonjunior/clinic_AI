export type Session = {
  token: string;
  roles: string[];
  tenantId: number;
};

const STORAGE_KEY = "nexusclin_session";

export function setSession(session: Session) {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
}

export const saveSession = setSession;

export function getSession(): Session | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw);
    return parsed;
  } catch {
    return null;
  }
}

export function clearSession() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(STORAGE_KEY);
}

export function isAuthenticated(): boolean {
  const session = getSession();
  return !!(session && session.token);
}

export function hasRole(session: Session | null, roles: string[]): boolean {
  if (!session) return false;
  return session.roles.some((r) => roles.includes(r));
}

export function authHeaders(session: Session | null): Record<string, string> {
  if (!session) return {};
  return { Authorization: `Bearer ${session.token}` };
}
