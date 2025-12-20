import Link from "next/link";

export default function Page() {
  const cards = [
    { href: "/dashboard", title: "Dashboard", desc: "Indicadores por unidade" },
    { href: "/agenda", title: "Agenda", desc: "Triagem, avaliacao, terapias" },
    { href: "/prontuario", title: "Prontuario", desc: "Evolucoes e Tiptap" },
    { href: "/producao", title: "Producao SUS", desc: "Procedimentos SIGTAP" },
    { href: "/auditoria", title: "Auditoria/Exportacao", desc: "BPA/APAC preview" },
  ];
  return (
    <main>
      <h1 className="text-3xl mb-4">NexusClin</h1>
      <p className="text-gray-300 mb-6 max-w-3xl">
        PEP multiprofissional + faturamento SUS com exportacao BPA-I/APAC nos layouts oficiais (Nov/2025).
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {cards.map((c) => (
          <Link key={c.href} href={c.href} className="card block hover:opacity-90 transition">
            <div className="text-xl mb-2">{c.title}</div>
            <div className="text-gray-400 text-sm">{c.desc}</div>
          </Link>
        ))}
      </div>
    </main>
  );
}
