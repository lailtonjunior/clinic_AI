"use client";

import { useState } from "react";
import { useLogin } from "../../lib/hooks/useAuth";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [tenantId, setTenantId] = useState("");
  const login = useLogin();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    login.mutate({
      email,
      password,
      tenant_id: Number(tenantId),
    });
  }

  const error = login.error instanceof Error ? login.error.message : login.error;

  return (
    <div className="mx-auto mt-12 max-w-md space-y-6">
      <h1 className="text-2xl font-semibold">Acesso NexusClin</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="email" className="block text-sm font-medium">
            Email
          </label>
          <input
            id="email"
            className="w-full rounded border px-3 py-2"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            aria-label="Email"
          />
        </div>
        <div>
          <label htmlFor="password" className="block text-sm font-medium">
            Senha
          </label>
          <input
            id="password"
            className="w-full rounded border px-3 py-2"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            aria-label="Senha"
          />
        </div>
        <div>
          <label htmlFor="tenantId" className="block text-sm font-medium">
            Tenant ID
          </label>
          <input
            id="tenantId"
            className="w-full rounded border px-3 py-2"
            type="number"
            value={tenantId}
            onChange={(e) => setTenantId(e.target.value)}
            required
            aria-label="Tenant ID"
          />
        </div>
        {error && <p className="text-sm text-red-600">{String(error)}</p>}
        <button
          type="submit"
          className="w-full rounded bg-blue-600 px-4 py-2 text-white disabled:opacity-60"
          disabled={login.isPending}
        >
          {login.isPending ? "Entrando..." : "Entrar"}
        </button>
      </form>
    </div>
  );
}
