"use client";
import { useEffect, useState } from "react";
import { createTenant, getTenants } from "../../../lib/api";
import { TenantTable } from "../../../components/tenants/TenantTable";
import { getSession, hasRole } from "../../../lib/auth";
import { useRouter } from "next/navigation";
import { Tenant } from "../../../lib/api";

export default function TenantsPage() {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  async function load() {
    try {
      const data = await getTenants();
      setTenants(data);
    } catch (err: any) {
      setError(err?.message || "Erro ao carregar tenants");
    }
  }

  useEffect(() => {
    const session = getSession();
    if (!hasRole(session, ["SUPER_ADMIN"])) {
      router.push("/login");
      return;
    }
    load();
  }, [router]);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    const form = e.target as HTMLFormElement;
    const data = new FormData(form);
    const name = data.get("name") as string;
    const cnpj = (data.get("cnpj") as string) || undefined;
    if (!name) return;
    await createTenant({ name, cnpj });
    form.reset();
    load();
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Tenants (SUPER_ADMIN)</h1>
      {error && <p className="text-red-600 text-sm">{error}</p>}
      <form onSubmit={handleCreate} className="space-x-2">
        <input name="name" className="border px-2 py-1" placeholder="Nome do tenant" required />
        <input name="cnpj" className="border px-2 py-1" placeholder="CNPJ (opcional)" />
        <button className="bg-blue-600 text-white px-3 py-1 rounded" type="submit">
          Criar tenant
        </button>
      </form>
      <TenantTable tenants={tenants} onRefresh={load} />
    </div>
  );
}
