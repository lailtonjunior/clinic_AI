const cards = [
  { label: "Atendimentos hoje", value: 42 },
  { label: "Procedimentos na competência", value: 380 },
  { label: "Pendências auditoria", value: 3 },
];

export default function DashboardPage() {
  return (
    <main>
      <h1 className="text-2xl mb-4">Dashboard por unidade</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {cards.map((c) => (
          <div key={c.label} className="card">
            <div className="text-sm text-gray-400">{c.label}</div>
            <div className="text-3xl font-semibold mt-2">{c.value}</div>
          </div>
        ))}
      </div>
    </main>
  );
}
