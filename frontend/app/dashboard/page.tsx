"use client";
import { useRouter } from "next/navigation";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";

const kpis = {
  pacientesMes: 128,
  procedimentosFaturaveis: 342,
  errosAuditoriaPendentes: 7,
  exportsRecentes: 5,
};

const producaoDiaria = [
  { dia: "Seg", valor: 65 },
  { dia: "Ter", valor: 78 },
  { dia: "Qua", valor: 54 },
  { dia: "Qui", valor: 90 },
  { dia: "Sex", valor: 72 },
  { dia: "Sáb", valor: 30 },
];

const atividadesRecentes = [
  { titulo: "Export BPA gerada para 202501", data: "Hoje, 14:32", cor: "bg-[#009739]" },
  { titulo: "Sync SIGTAP concluído", data: "Hoje, 10:05", cor: "bg-[#004A8F]" },
  { titulo: "Novo paciente cadastrado", data: "Ontem, 16:40", cor: "bg-emerald-500" },
  { titulo: "APAC enviada para auditoria", data: "Ontem, 11:12", cor: "bg-[#FFCC29]" },
];

export default function DashboardPage() {
  const router = useRouter();

  return (
    <main className="mx-auto max-w-7xl px-4 py-6 space-y-6">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold text-slate-100">Dashboard Clínico e Faturamento</h1>
        <p className="text-sm text-slate-400">
          Visão geral da produção SUS, auditoria e exportações BPA/APAC na competência atual.
        </p>
      </header>

      <section
        aria-label="Indicadores principais"
        className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4"
      >
        <KpiCard
          label="Pacientes atendidos no mês"
          value={kpis.pacientesMes}
          accent="text-[#009739]"
          hint="Comparado ao mês anterior: +12%"
        />
        <KpiCard
          label="Procedimentos SUS faturáveis"
          value={kpis.procedimentosFaturaveis}
          accent="text-[#004A8F]"
          hint="Inclui BPA-I e APAC da competência"
        />
        <KpiCard
          label="Erros de auditoria pendentes"
          value={kpis.errosAuditoriaPendentes}
          accent="text-[#FFCC29]"
          hint="Revise a fila de auditoria"
        />
        <KpiCard
          label="Exportações geradas (BPA/APAC)"
          value={kpis.exportsRecentes}
          accent="text-emerald-400"
          hint="Últimos 7 dias"
        />
      </section>

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <div className="xl:col-span-2 rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-semibold text-slate-100">Produção por dia (competência atual)</h2>
              <p className="text-sm text-slate-400">Procedimentos faturáveis registrados por dia útil.</p>
            </div>
            <Badge className="border border-[#004A8F] bg-transparent text-[#004A8F]">
              Competência 202501
            </Badge>
          </div>
          <div className="h-40 flex items-end gap-3 rounded-xl border border-slate-800 bg-slate-950 px-4 py-4">
            {producaoDiaria.map((p) => (
              <div key={p.dia} className="flex flex-col items-center gap-2">
                <div
                  className="w-5 rounded-t-md bg-gradient-to-t from-[#004A8F] to-[#009739] shadow-[0_4px_12px_rgba(0,151,57,0.25)]"
                  style={{ height: `${p.valor}%`, minHeight: "1.5rem" }}
                />
                <span className="text-xs text-slate-400">{p.dia}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
          <h2 className="text-lg font-semibold text-slate-100 mb-3">Atividades recentes</h2>
          <div className="space-y-4">
            {atividadesRecentes.map((item, idx) => (
              <div key={idx} className="flex gap-3">
                <span className={`mt-1 h-3 w-3 rounded-full ${item.cor}`} aria-hidden />
                <div className="space-y-1">
                  <div className="text-sm font-medium text-slate-100">{item.titulo}</div>
                  <div className="text-xs text-slate-400">{item.data}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
          <h3 className="text-lg font-semibold text-slate-100 mb-2">Resumo do Assistente Clínico</h3>
          <p className="text-sm text-slate-300 leading-relaxed">
            O Assistente apoia condutas clínicas, validação SIGTAP e preenchimento de BPA/APAC. Disponível nas telas de
            Prontuário e Produção para acelerar o faturamento com segurança.
          </p>
          <p className="mt-2 text-xs text-slate-500">
            Não substitui a decisão do profissional; revise sempre antes de confirmar.
          </p>
          <div className="mt-4 flex flex-wrap gap-3">
            <Button
              className="bg-[#009739] hover:bg-emerald-600 text-white"
              onClick={() => router.push("/producao")}
            >
              Ir para Produção
            </Button>
            <Button
              variant="outline"
              className="border-[#004A8F] text-[#004A8F] hover:bg-[#004A8F]/10"
              onClick={() => router.push("/prontuario")}
            >
              Ir para Prontuário
            </Button>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
          <h3 className="text-lg font-semibold text-slate-100 mb-2">Checklist rápido</h3>
          <ul className="space-y-2 text-sm text-slate-300">
            <li className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-[#009739]" /> Revisar auditoria pendente ({kpis.errosAuditoriaPendentes})
            </li>
            <li className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-[#004A8F]" /> Confirmar exportações geradas ({kpis.exportsRecentes})
            </li>
            <li className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-[#FFCC29]" /> Validar produção diária e SIGTAP
            </li>
          </ul>
        </div>
      </section>
    </main>
  );
}

type KpiCardProps = {
  label: string;
  value: number | string;
  accent: string;
  hint?: string;
};

function KpiCard({ label, value, accent, hint }: KpiCardProps) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4 shadow-lg shadow-black/30">
      <div className="text-xs uppercase tracking-wide text-slate-400">{label}</div>
      <div className={`mt-2 text-3xl font-semibold ${accent}`}>{value}</div>
      {hint && <div className="text-xs text-slate-500 mt-1">{hint}</div>}
    </div>
  );
}
