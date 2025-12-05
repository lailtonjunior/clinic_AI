"use client";

type AuditErro = { procedimento_id: number; erros: string[] };

type Props = {
  status: "pending" | "ok" | "error";
  erros: AuditErro[];
};

export function AuditoriaResultado({ status, erros }: Props) {
  if (status === "pending") {
    return <div className="text-sm text-slate-400">Rodar auditoria para ver pendências.</div>;
  }

  if (status === "ok") {
    return (
      <div className="border border-emerald-600 bg-emerald-950/40 text-emerald-200 rounded px-3 py-2 text-sm">
        Competência pronta para exportação (sem pendências).
      </div>
    );
  }

  if (erros.length === 0) {
    return (
      <div className="border border-amber-500 bg-amber-900/40 text-amber-100 rounded px-3 py-2 text-sm">
        Auditoria executada, mas nenhum erro listado foi retornado.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="border border-rose-600 bg-rose-950/40 text-rose-100 rounded px-3 py-2 text-sm">
        Foram encontrados erros; ajuste antes de exportar.
      </div>
      <div className="border border-slate-800 rounded">
        <div className="grid grid-cols-3 text-xs text-slate-400 border-b border-slate-800 px-3 py-2">
          <span>Procedimento</span>
          <span className="col-span-2">Erros</span>
        </div>
        <div className="divide-y divide-slate-800 text-sm">
          {erros.map((e) => (
            <div key={e.procedimento_id} className="grid grid-cols-3 px-3 py-2">
              <span className="text-slate-200">#{e.procedimento_id}</span>
              <span className="col-span-2 text-amber-200">{e.erros.join(", ")}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
