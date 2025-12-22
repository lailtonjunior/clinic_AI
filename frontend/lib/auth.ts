export type Session = {
  token: string;
  roles: string[];
  tenantId: number;
};

const STORAGE_KEY = "nexusclin_session";
const TOKEN_COOKIE_KEY = "nexusclin_token";

export function setSession(session: Session) {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  
  // Also save token in cookie for middleware access
  // Cookie expires in 7 days (same as typical JWT expiry)
  const expires = new Date();
  expires.setDate(expires.getDate() + 7);
  document.cookie = `${TOKEN_COOKIE_KEY}=${session.token}; path=/; expires=${expires.toUTCString()}; SameSite=Lax`;
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
  
  // Clear cookie as well
  document.cookie = `${TOKEN_COOKIE_KEY}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT`;
}

export function getTokenFromCookie(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(new RegExp(`(^| )${TOKEN_COOKIE_KEY}=([^;]+)`));
  return match ? match[2] : null;
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
