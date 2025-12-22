"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { ReactNode } from "react";

import { hasRole } from "../lib/auth";
import { useSession, useLogout } from "../lib/hooks/useAuth";
import { NotificationsProvider } from "./ui/notifications";

type Props = { children: ReactNode };

export function AppShell({ children }: Props) {
  const { data: session } = useSession();
  const logout = useLogout();
  const router = useRouter();

  // Middleware handles auth redirects, so session should always exist here (except login page)
  const showRecepcao = session ? hasRole(session, ["RECEPCAO", "ADMIN_TENANT"]) : false;
  const showClinico = session ? hasRole(session, ["CLINICO", "ADMIN_TENANT"]) : false;
  const showFaturamento = session ? hasRole(session, ["FATURAMENTO", "ADMIN_TENANT", "SUPER_ADMIN"]) : false;
  const showAuditoria = session ? hasRole(session, ["FATURAMENTO", "ADMIN_TENANT", "SUPER_ADMIN", "AUDITOR_INTERNO"]) : false;
  const showConfig = session ? hasRole(session, ["ADMIN_TENANT", "SUPER_ADMIN"]) : false;
  const showTenants = session ? hasRole(session, ["SUPER_ADMIN"]) : false;

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

  const handleLogout = () => {
    logout.mutate();
  };

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
                  type="button"
                  className="underline"
                  onClick={handleLogout}
                  disabled={logout.isPending}
                >
                  {logout.isPending ? "Saindo..." : "Sair"}
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
