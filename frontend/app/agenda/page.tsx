"use client";
import { useEffect, useMemo, useState } from "react";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeaderCell, TableRow } from "../../components/ui/table";
import { useNotifications } from "../../components/ui/notifications";
import { getAgendas, updateAgenda } from "../../lib/api";

const hours = Array.from({ length: 10 }, (_, i) => 8 + i); // 08-17h

function startOfWeek(date: Date) {
  const d = new Date(date);
  const day = d.getDay();
  const diff = d.getDate() - day + (day === 0 ? -6 : 1); // monday as first
  d.setDate(diff);
  d.setHours(0, 0, 0, 0);
  return d;
}

const statusVariants: Record<string, "default" | "success" | "warning" | "danger"> = {
  livre: "default",
  agendado: "warning",
  concluido: "success",
  faltou: "danger",
};

export default function AgendaPage() {
  const { notifyError, notifySuccess } = useNotifications();
  const [agendas, setAgendas] = useState<any[]>([]);
  const [draggingId, setDraggingId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  const weekStart = useMemo(() => startOfWeek(new Date()), []);
  const days = useMemo(() => Array.from({ length: 7 }, (_, i) => new Date(weekStart.getTime() + i * 86400000)), [weekStart]);

  useEffect(() => {
    async function load() {
      try {
        const data = await getAgendas();
        setAgendas(data);
      } catch (err: any) {
        notifyError(err?.message || "Erro ao carregar agenda");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [notifyError]);

  const byDay = useMemo(() => {
    const map: Record<string, any[]> = {};
    days.forEach((d) => (map[d.toDateString()] = []));
    agendas.forEach((ag) => {
      const dt = new Date(ag.data);
      const key = dt.toDateString();
      if (map[key]) map[key].push({ ...ag, dateObj: dt });
    });
    return map;
  }, [agendas, days]);

  async function handleDrop(day: Date, hour: number) {
    if (draggingId === null) return;
    const newDate = new Date(day);
    newDate.setHours(hour, 0, 0, 0);
    try {
      await updateAgenda(draggingId, { data: newDate.toISOString() });
      notifySuccess("Agendamento atualizado");
      setAgendas((prev) => prev.map((a) => (a.id === draggingId ? { ...a, data: newDate.toISOString() } : a)));
    } catch (err: any) {
      notifyError(err?.message || "Erro ao reagendar");
    } finally {
      setDraggingId(null);
    }
  }

  return (
    <main className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Agenda semanal</h1>
      </div>

      <div className="overflow-auto rounded-lg border border-slate-800 bg-slate-900/60">
        <Table className="min-w-[800px]">
          <TableHead>
            <TableRow>
              <TableHeaderCell>Hora</TableHeaderCell>
              {days.map((d) => (
                <TableHeaderCell key={d.toDateString()}>{d.toLocaleDateString("pt-BR", { weekday: "short", day: "2-digit", month: "2-digit" })}</TableHeaderCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {hours.map((h) => (
              <TableRow key={h}>
                <TableCell className="font-semibold">{String(h).padStart(2, "0")}:00</TableCell>
                {days.map((d) => {
                  const key = d.toDateString();
                  const items = (byDay[key] || []).filter((ag) => new Date(ag.data).getHours() === h);
                  return (
                    <TableCell
                      key={key + h}
                      onDragOver={(e) => e.preventDefault()}
                      onDrop={() => handleDrop(d, h)}
                      className="min-h-[72px] align-top"
                    >
                      {items.map((ag) => (
                        <div
                          key={ag.id}
                          draggable
                          onDragStart={() => setDraggingId(ag.id)}
                          className="mb-2 cursor-move rounded border border-slate-700 bg-slate-800 p-2 text-xs shadow"
                        >
                          <div className="flex items-center justify-between">
                            <span>{ag.tipo}</span>
                            <Badge variant={statusVariants[ag.status] || "default"}>{ag.status}</Badge>
                          </div>
                          <div className="text-slate-300">Profissional #{ag.profissional_id}</div>
                          {ag.paciente_id && <div className="text-slate-400">Paciente #{ag.paciente_id}</div>}
                        </div>
                      ))}
                      {!items.length && <div className="text-[11px] text-slate-600">Arraste aqui para remarcação</div>}
                    </TableCell>
                  );
                })}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      {loading && <div className="text-sm text-slate-400">Carregando...</div>}
    </main>
  );
}
