const agenda = [
  { hora: "08:00", profissional: "Fisio - Ana", paciente: "João", tipo: "avaliação" },
  { hora: "09:00", profissional: "TO - Carla", paciente: "Maria", tipo: "terapia" },
  { hora: "10:00", profissional: "Fono - Luiza", paciente: "Pedro", tipo: "reavaliação" },
];

export default function AgendaPage() {
  return (
    <main>
      <h1 className="text-2xl mb-4">Agenda multiprofissional</h1>
      <div className="space-y-3">
        {agenda.map((slot) => (
          <div key={slot.hora} className="card flex items-center justify-between">
            <div>
              <div className="text-lg">{slot.hora}</div>
              <div className="text-gray-400 text-sm">{slot.tipo}</div>
            </div>
            <div className="text-right">
              <div>{slot.profissional}</div>
              <div className="text-gray-400 text-sm">{slot.paciente}</div>
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}
