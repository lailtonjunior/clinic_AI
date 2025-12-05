"use client";
import { useEffect, useState } from "react";
import { changePassword } from "../../lib/api";
import { getSession } from "../../lib/auth";
import { useRouter } from "next/navigation";

export default function PerfilPage() {
  const [senhaAtual, setSenhaAtual] = useState("");
  const [senhaNova, setSenhaNova] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const session = getSession();
    if (!session) {
      router.push("/login");
    }
  }, [router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setMsg(null);
    setError(null);
    try {
      await changePassword({ senha_atual: senhaAtual, senha_nova: senhaNova });
      setMsg("Senha alterada com sucesso.");
      setSenhaAtual("");
      setSenhaNova("");
    } catch (err: any) {
      setError(err?.message || "Erro ao alterar senha");
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Meu perfil</h1>
      <form onSubmit={handleSubmit} className="space-y-3 max-w-md">
        <div>
          <label className="block text-sm font-medium">Senha atual</label>
          <input className="border rounded px-3 py-2 w-full" type="password" value={senhaAtual} onChange={(e) => setSenhaAtual(e.target.value)} required />
        </div>
        <div>
          <label className="block text-sm font-medium">Nova senha</label>
          <input className="border rounded px-3 py-2 w-full" type="password" value={senhaNova} onChange={(e) => setSenhaNova(e.target.value)} required />
        </div>
        {msg && <p className="text-green-600 text-sm">{msg}</p>}
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <button className="bg-blue-600 text-white px-4 py-2 rounded" type="submit">
          Alterar senha
        </button>
      </form>
    </div>
  );
}
