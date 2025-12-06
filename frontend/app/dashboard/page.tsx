"use client";
import { useEffect, useState } from "react";
import { Badge } from "../../components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeaderCell, TableRow } from "../../components/ui/table";
import { useNotifications } from "../../components/ui/notifications";
import { DashboardResponse, getDashboard } from "../../lib/api";

export default function DashboardPage() {
  const { notifyError } = useNotifications();
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const resp = await getDashboard();
        setData(resp);
      } catch (err: any) {
        notifyError(err?.message || "Erro ao carregar dashboard");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [notifyError]);

  const cards = [
    { label: "Atendimentos no mês", value: data?.total_atendimentos ?? "..." },
    { label: "Pacientes únicos", value: data?.total_pacientes ?? "..." },
    { label: "Procedimentos", value: data?.total_procedimentos ?? "..." },
    { label: "Erros de auditoria", value: data?.total_procedimentos_com_erro ?? "..." },
  ];

  return (
    <main className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Dashboard da competência atual</h1>
          {data?.competencia && <p className="text-sm text-slate-400">Competência: {data.competencia}</p>}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        {cards.map((c) => (
          <div key={c.label} className="rounded-lg border border-slate-800 bg-slate-900/60 p-4">
            <div className="text-sm text-slate-400">{c.label}</div>
            <div className="mt-2 text-3xl font-semibold">
              {loading ? <span className="block h-6 w-16 animate-pulse rounded bg-slate-800" /> : c.value}
            </div>
          </div>
        ))}
      </div>

      <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-4">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Últimas exportações BPA/APAC</h2>
        </div>
        {loading ? (
          <div className="h-20 animate-pulse rounded bg-slate-800" />
        ) : (
          <Table>
            <TableHead>
              <TableRow>
                <TableHeaderCell>ID</TableHeaderCell>
                <TableHeaderCell>Tipo</TableHeaderCell>
                <TableHeaderCell>Competência</TableHeaderCell>
                <TableHeaderCell>Status</TableHeaderCell>
                <TableHeaderCell>Erros</TableHeaderCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data?.ultimas_exportacoes?.length ? (
                data.ultimas_exportacoes.map((exp) => (
                  <TableRow key={`${exp.tipo}-${exp.id}`}>
                    <TableCell>{exp.id}</TableCell>
                    <TableCell>{exp.tipo}</TableCell>
                    <TableCell>{exp.competencia}</TableCell>
                    <TableCell>
                      <Badge variant={exp.status === "gerado" ? "success" : "warning"}>{exp.status}</Badge>
                    </TableCell>
                    <TableCell>
                      {exp.erros && Object.keys(exp.erros).length ? (
                        <Badge variant="danger">Com erros</Badge>
                      ) : (
                        <Badge variant="default">Nenhum</Badge>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-slate-400">
                    Nenhuma exportação registrada.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        )}
      </div>
    </main>
  );
}
