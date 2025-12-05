"use client";
import { useState } from "react";
import { createUser } from "../../lib/api";

type Props = { onCreated: () => void };

export function UserForm({ onCreated }: Props) {
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [roles, setRoles] = useState<string>("CLINICO");
  const [mustChange, setMustChange] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await createUser({ nome, email, senha, roles: roles.split(",").map((r) => r.trim()), must_change_password: mustChange });
      setNome("");
      setEmail("");
      setSenha("");
      setRoles("CLINICO");
      onCreated();
    } catch (err: any) {
      setError(err?.message || "Erro ao criar usuário");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3 border p-4 rounded">
      <div>
        <label className="block text-sm font-medium">Nome</label>
        <input className="border rounded px-3 py-2 w-full" value={nome} onChange={(e) => setNome(e.target.value)} required />
      </div>
      <div>
        <label className="block text-sm font-medium">Email</label>
        <input className="border rounded px-3 py-2 w-full" value={email} onChange={(e) => setEmail(e.target.value)} required />
      </div>
      <div>
        <label className="block text-sm font-medium">Senha inicial</label>
        <input className="border rounded px-3 py-2 w-full" type="password" value={senha} onChange={(e) => setSenha(e.target.value)} required />
      </div>
      <div>
        <label className="block text-sm font-medium">Roles (separadas por vírgula)</label>
        <input className="border rounded px-3 py-2 w-full" value={roles} onChange={(e) => setRoles(e.target.value)} />
      </div>
      <div className="flex items-center space-x-2">
        <input type="checkbox" checked={mustChange} onChange={(e) => setMustChange(e.target.checked)} />
        <span className="text-sm">Forçar troca de senha no primeiro login</span>
      </div>
      {error && <p className="text-red-600 text-sm">{error}</p>}
      <button className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-60" type="submit" disabled={loading}>
        {loading ? "Salvando..." : "Criar usuário"}
      </button>
    </form>
  );
}
