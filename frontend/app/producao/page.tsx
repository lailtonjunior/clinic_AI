import Link from "next/link";

const procedimentos = [
  { atendimento: "ATD-001", sigtap: "0301010010", cid: "F329", quantidade: 1, status: "validado" },
  { atendimento: "ATD-002", sigtap: "0301010029", cid: "G450", quantidade: 2, status: "pendente" },
];

function competenciaAtual(): string {
  const now = new Date();
  const ano = now.getFullYear();
  const mes = String(now.getMonth() + 1).padStart(2, "0");
  return `${ano}${mes}`;
}

export default function ProducaoPage() {
  const cmp = competenciaAtual();
  return (
    <main className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl">Produção SUS</h1>
        <Link
          href={`/auditoria?competencia=${cmp}`}
          className="px-4 py-2 bg-sky-600 rounded text-sm hover:bg-sky-500 transition"
        >
          Auditar e Exportar Produção
        </Link>
      </div>
      <div className="card">
        <table className="w-full text-sm">
          <thead className="text-gray-400">
            <tr>
              <th className="text-left">Atendimento</th>
              <th className="text-left">SIGTAP</th>
              <th className="text-left">CID</th>
              <th className="text-left">Qtd</th>
              <th className="text-left">Status</th>
            </tr>
          </thead>
          <tbody>
            {procedimentos.map((p) => (
              <tr key={p.atendimento} className="border-b border-slate-800">
                <td>{p.atendimento}</td>
                <td>{p.sigtap}</td>
                <td>{p.cid}</td>
                <td>{p.quantidade}</td>
                <td className={p.status === "validado" ? "text-green-400" : "text-amber-400"}>{p.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}
