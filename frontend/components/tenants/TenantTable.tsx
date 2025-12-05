"use client";
import { updateTenant } from "../../lib/api";

type Tenant = { id: number; name: string; cnpj?: string };

type Props = { tenants: Tenant[]; onRefresh: () => void };

export function TenantTable({ tenants, onRefresh }: Props) {
  async function handleRename(id: number) {
    const name = prompt("Novo nome do tenant:");
    if (!name) return;
    await updateTenant(id, { name });
    onRefresh();
  }

  return (
    <table className="w-full border text-sm">
      <thead>
        <tr className="bg-gray-100">
          <th className="p-2 text-left">ID</th>
          <th className="p-2 text-left">Nome</th>
          <th className="p-2 text-left">CNPJ</th>
          <th className="p-2">Ações</th>
        </tr>
      </thead>
      <tbody>
        {tenants.map((t) => (
          <tr key={t.id} className="border-t">
            <td className="p-2">{t.id}</td>
            <td className="p-2">{t.name}</td>
            <td className="p-2">{t.cnpj || "-"}</td>
            <td className="p-2">
              <button className="underline text-blue-600" onClick={() => handleRename(t.id)}>
                Renomear
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
