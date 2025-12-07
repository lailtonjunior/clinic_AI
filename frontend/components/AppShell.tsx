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
      router.push("/dashboard");
    }
  }, [pathname, router]);

  const showRecepcao = hasRole(session, ["RECEPCAO", "ADMIN_TENANT"]);
  const showClinico = hasRole(session, ["CLINICO", "ADMIN_TENANT"]);
  const showFaturamento = hasRole(session, ["FATURAMENTO", "ADMIN_TENANT", "SUPER_ADMIN"]);
  const showAuditoria = hasRole(session, ["FATURAMENTO", "ADMIN_TENANT", "SUPER_ADMIN", "AUDITOR_INTERNO"]);
  const showConfig = hasRole(session, ["ADMIN_TENANT", "SUPER_ADMIN"]);
  const showTenants = hasRole(session, ["SUPER_ADMIN"]);

  const links = [
    { href: "/dashboard", label: "Dashboard", show: true },
    { href: "/agenda", label: "Agenda", show: showRecepcao },
    { href: "/prontuario", label: "Prontuário", show: showClinico },
    { href: "/producao", label: "Produção", show: showFaturamento },
    { href: "/auditoria", label: "Auditoria", show: showAuditoria },
    { href: "/config/usuarios", label: "Usuários", show: showConfig },
    { href: "/config/tenants", label: "Tenants", show: showTenants },
    { href: "/perfil", label: "Perfil", show: true },
  ].filter((link) => link.show);

  return (
    <NotificationsProvider>
      <div className="flex min-h-screen flex-col bg-slate-950 text-slate-100">
        <header className="flex items-center justify-between border-b border-slate-800 px-6 py-4">
          <nav className="flex flex-wrap items-center gap-3 text-sm font-semibold">
            {links.map((link) => (
              <Link key={link.href} href={link.href} className="hover:text-sky-300">
                {link.label}
              </Link>
            ))}
          </nav>
          <div className="flex items-center gap-3 text-xs text-slate-400">
            {session ? (
              <>
                <span>Tenant #{session.tenantId}</span>
                <span>{session.roles.join(", ")}</span>
                <button
                  className="underline"
                  onClick={() => {
                    clearSession();
                    setSession(null);
                    router.push("/login");
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
        <main className="flex-1 px-6 py-6">{children}</main>
      </div>
    </NotificationsProvider>
  );
}
