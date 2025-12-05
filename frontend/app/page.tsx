import Link from "next/link";

export default function Page() {
  const cards = [
    { href: "/dashboard", title: "Dashboard", desc: "Indicadores por unidade" },
    { href: "/agenda", title: "Agenda", desc: "Triagem, avaliação, terapias" },
    { href: "/prontuario", title: "Prontuário", desc: "Evoluções e Tiptap" },
    { href: "/producao", title: "Produção SUS", desc: "Procedimentos SIGTAP" },
    { href: "/auditoria", title: "Auditoria/Exportação", desc: "BPA/APAC preview" },
  ];
  return (
    <main>
      <h1 className="text-3xl mb-4">NexusClin</h1>
      <p className="text-gray-300 mb-6 max-w-3xl">
        PEP multiprofissional + faturamento SUS com exportação BPA-I/APAC nos layouts oficiais (Nov/2025).
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
