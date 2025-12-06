"use client";
import { useState } from "react";
import { createUser } from "../../lib/api";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { useNotifications } from "../ui/notifications";

type Props = { onCreated: () => void };

const roleOptions = [
  "SUPER_ADMIN",
  "ADMIN_TENANT",
  "FATURAMENTO",
  "CLINICO",
  "RECEPCAO",
  "AUDITOR_INTERNO",
];

export function UserForm({ onCreated }: Props) {
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [roles, setRoles] = useState<string[]>(["CLINICO"]);
  const [mustChange, setMustChange] = useState(true);
  const [loading, setLoading] = useState(false);
  const { notifySuccess, notifyError } = useNotifications();

  const toggleRole = (role: string) => {
    setRoles((prev) => (prev.includes(role) ? prev.filter((r) => r !== role) : [...prev, role]));
  };

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await createUser({ nome, email, senha, roles, must_change_password: mustChange });
      setNome("");
      setEmail("");
      setSenha("");
      setRoles(["CLINICO"]);
      notifySuccess("Usuário criado com sucesso");
      onCreated();
    } catch (err: any) {
      notifyError(err?.message || "Erro ao criar usuário");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded border border-slate-800 bg-slate-900/60 p-4">
      <Input label="Nome" value={nome} onChange={(e) => setNome(e.target.value)} required />
      <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
      <Input label="Senha inicial" type="password" value={senha} onChange={(e) => setSenha(e.target.value)} required />

      <div className="space-y-2">
        <div className="text-sm text-slate-200">Roles (seleção múltipla)</div>
        <div className="grid grid-cols-2 gap-2 md:grid-cols-3">
          {roleOptions.map((role) => (
            <label key={role} className="flex items-center gap-2 rounded border border-slate-800 px-3 py-2 text-sm">
              <input
                type="checkbox"
                checked={roles.includes(role)}
                onChange={() => toggleRole(role)}
                className="h-4 w-4 accent-sky-500"
              />
              <span>{role}</span>
            </label>
          ))}
        </div>
      </div>

      <label className="flex items-center gap-2 text-sm text-slate-200">
        <input
          type="checkbox"
          checked={mustChange}
          onChange={(e) => setMustChange(e.target.checked)}
          className="h-4 w-4 accent-sky-500"
        />
        <span>Forçar troca de senha no primeiro login</span>
      </label>

      <Button type="submit" disabled={loading}>
        {loading ? "Salvando..." : "Criar usuário"}
      </Button>
    </form>
  );
}
