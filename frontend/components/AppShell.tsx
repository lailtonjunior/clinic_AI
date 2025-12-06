"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ReactNode, useEffect, useState } from "react";
import { clearSession, getSession, hasRole, isAuthenticated, Session } from "../lib/auth";
import { NotificationsProvider } from "./ui/notifications";

type Props = { children: ReactNode };

export function AppShell({ children }: Props) {
  const [session, setSession] = useState<Session | null>(null);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const sess = getSession();
    setSession(sess);
    if (!isAuthenticated() && pathname !== "/login") {
        router.push("/login");
    }
    if (sess && pathname === "/login") {
        router.push("/producao");
    }
  }, [pathname, router]);

  const showFaturamento = hasRole(session, ["FATURAMENTO", "ADMIN_TENANT", "SUPER_ADMIN"]);
  const showAuditoria = hasRole(session, ["FATURAMENTO", "ADMIN_TENANT", "SUPER_ADMIN", "AUDITOR_INTERNO"]);
  const showClinico = hasRole(session, ["CLINICO", "ADMIN_TENANT"]);
  const showRecepcao = hasRole(session, ["RECEPCAO", "ADMIN_TENANT"]);
  const showConfig = hasRole(session, ["ADMIN_TENANT", "SUPER_ADMIN"]);
  const showTenants = hasRole(session, ["SUPER_ADMIN"]);

  return (
    <NotificationsProvider>
      <div className="max-w-7xl mx-auto px-6 py-6 space-y-6">
        <header className="flex items-center justify-between">
          <div className="space-x-4 text-sm font-semibold">
            <Link href="/">Dashboard</Link>
            {showRecepcao && <Link href="/agenda">Agenda</Link>}
            {showClinico && <Link href="/prontuario">Prontuário</Link>}
            {showFaturamento && <Link href="/producao">Produção</Link>}
            {showAuditoria && <Link href="/auditoria">Auditoria</Link>}
            {showConfig && <Link href="/config/usuarios">Usuários</Link>}
            {showTenants && <Link href="/config/tenants">Tenants</Link>}
            <Link href="/perfil">Perfil</Link>
          </div>
          <div className="text-xs text-gray-600 space-x-3">
            {session ? (
              <>
                <span>Tenant #{session.tenantId}</span>
                <span>{session.roles.join(", ")}</span>
                <button
                  className="underline"
                  onClick={() => {
                    clearSession();
                    setSession(null);
                  }}
                >
                  Sair
                </button>
              </>
            ) : (
              <Link href="/login" className="underline">
                Entrar
              </Link>
            )}
          </div>
        </header>
        <div>{children}</div>
      </div>
    </NotificationsProvider>
  );
}
