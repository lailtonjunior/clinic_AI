"use client";
import { resetUserPassword, updateUser } from "../../lib/api";

type Props = {
  users: { id: number; nome: string; email: string; roles: string[]; ativo: boolean; must_change_password: boolean }[];
  onRefresh: () => void;
};

export function UserTable({ users, onRefresh }: Props) {
  async function handleReset(id: number) {
    await resetUserPassword(id, {});
    onRefresh();
  }

  async function toggleActive(id: number, ativo: boolean) {
    await updateUser(id, { is_active: !ativo });
    onRefresh();
  }

  return (
    <table className="w-full border text-sm">
      <thead>
        <tr className="bg-gray-100">
          <th className="p-2 text-left">Nome</th>
          <th className="p-2 text-left">Email</th>
          <th className="p-2 text-left">Roles</th>
          <th className="p-2 text-left">Ativo</th>
          <th className="p-2 text-left">Must Change Password</th>
          <th className="p-2">Ações</th>
        </tr>
      </thead>
      <tbody>
        {users.map((u) => (
          <tr key={u.id} className="border-t">
            <td className="p-2">{u.nome}</td>
            <td className="p-2">{u.email}</td>
            <td className="p-2">{u.roles.join(", ")}</td>
            <td className="p-2">{u.ativo ? "Sim" : "Não"}</td>
            <td className="p-2">{u.must_change_password ? "Sim" : "Não"}</td>
            <td className="p-2 space-x-2">
              <button className="underline text-blue-600" onClick={() => handleReset(u.id)}>
                Reset senha
              </button>
              <button className="underline text-blue-600" onClick={() => toggleActive(u.id, u.ativo)}>
                {u.ativo ? "Desativar" : "Ativar"}
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
