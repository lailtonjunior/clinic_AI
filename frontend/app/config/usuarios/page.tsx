"use client";
import { useEffect, useState } from "react";
import { createUser, getUsers } from "../../../lib/api";
import { UserTable } from "../../../components/users/UserTable";
import { UserForm } from "../../../components/users/UserForm";
import { getSession, hasRole } from "../../../lib/auth";
import { useRouter } from "next/navigation";
import { User } from "../../../lib/api";

export default function UsuariosPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  async function load() {
    try {
      const data = await getUsers();
      setUsers(data);
    } catch (err: any) {
      setError(err?.message || "Erro ao carregar usuários");
    }
  }

  useEffect(() => {
    const session = getSession();
    if (!hasRole(session, ["ADMIN_TENANT", "SUPER_ADMIN"])) {
      router.push("/login");
      return;
    }
    load();
  }, [router]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Usuários do Tenant</h1>
      {error && <p className="text-red-600 text-sm">{error}</p>}
      <UserForm onCreated={load} />
      <UserTable users={users} onRefresh={load} />
    </div>
  );
}
