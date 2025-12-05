"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { saveSession } from "../../lib/auth";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [tenantId, setTenantId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, tenant_id: Number(tenantId) }),
      });
      if (!res.ok) {
        const msg = await res.text();
        throw new Error(msg || "Falha no login");
      }
      const data = await res.json();
      saveSession({ token: data.access_token, roles: data.roles, tenantId: data.tenant_id });
      router.push("/producao");
    } catch (err: any) {
      const msg = err?.message || "Erro ao autenticar";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-md mx-auto mt-12 space-y-6">
      <h1 className="text-2xl font-semibold">Acesso NexusClin</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium">Email</label>
          <input
            className="border rounded px-3 py-2 w-full"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium">Senha</label>
          <input
            className="border rounded px-3 py-2 w-full"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium">Tenant ID</label>
          <input
            className="border rounded px-3 py-2 w-full"
            type="number"
            value={tenantId}
            onChange={(e) => setTenantId(e.target.value)}
            required
          />
        </div>
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <button
            type="submit"
            className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-60"
            disabled={loading}
        >
          {loading ? "Entrando..." : "Entrar"}
        </button>
      </form>
    </div>
  );
}
