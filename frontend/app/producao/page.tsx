"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeaderCell, TableRow } from "../../components/ui/table";
import { useNotifications } from "../../components/ui/notifications";
import { ExportItem, getExports, retryExport } from "../../lib/api";
import { AssistantChat } from "../../components/clinical/AssistantChat";

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
  const { notifyError, notifySuccess } = useNotifications();
  const [exportsBpa, setExportsBpa] = useState<ExportItem[]>([]);
  const [exportsApac, setExportsApac] = useState<ExportItem[]>([]);
  const [showErrors, setShowErrors] = useState<any | null>(null);
  const [showAssistant, setShowAssistant] = useState(false);

  async function loadExports() {
    try {
      const [bpa, apac] = await Promise.all([getExports("bpa"), getExports("apac")]);
      setExportsBpa(bpa);
      setExportsApac(apac);
    } catch (err: any) {
      notifyError(err?.message || "Erro ao carregar exportacoes");
    }
  }

  useEffect(() => {
    loadExports();
  }, []);

  async function handleRetry(tipo: "bpa" | "apac", id: number) {
    try {
      await retryExport(tipo, id);
      notifySuccess("Exportacao reprocessada");
      loadExports();
    } catch (err: any) {
      notifyError(err?.message || "Erro ao reprocessar exportacao");
    }
  }

  const renderTable = (items: any[], tipo: "bpa" | "apac") => (
    <Table>
      <TableHead>
        <TableRow>
          <TableHeaderCell>ID</TableHeaderCell>
          <TableHeaderCell>Competencia</TableHeaderCell>
          <TableHeaderCell>Status</TableHeaderCell>
          <TableHeaderCell>Arquivo</TableHeaderCell>
          <TableHeaderCell className="text-right">Acoes</TableHeaderCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {items.length === 0 ? (
          <TableRow>
            <TableCell colSpan={5} className="text-center text-slate-400">
              Nenhuma exportacao encontrada.
            </TableCell>
          </TableRow>
        ) : (
          items.map((exp) => (
            <TableRow key={exp.id}>
              <TableCell>{exp.id}</TableCell>
              <TableCell>{exp.competencia}</TableCell>
              <TableCell>
                <Badge variant={exp.status === "gerado" ? "success" : exp.status === "erro" ? "danger" : "warning"}>
                  {exp.status}
                </Badge>
              </TableCell>
              <TableCell className="text-xs break-all">{exp.arquivo_path}</TableCell>
              <TableCell className="space-x-2 text-right">
                <Button variant="outline" onClick={() => setShowErrors(exp.erros_json || {})}>
                  Detalhes
                </Button>
                <Button variant="secondary" onClick={() => handleRetry(tipo, exp.id)}>
                  Reprocessar
                </Button>
              </TableCell>
            </TableRow>
          ))
        )}
      </TableBody>
    </Table>
  );

  return (
    <main className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl">Producao SUS</h1>
        <div className="flex items-center gap-2">
          <Link href={`/auditoria?competencia=${cmp}`} className="px-4 py-2 bg-sky-600 rounded text-sm hover:bg-sky-500 transition">
            Auditar e Exportar Producao
          </Link>
          <Button variant="secondary" onClick={() => setShowAssistant(true)}>
            Assistente Clinico
          </Button>
        </div>
      </div>
      <div className="card">
        <Table className="w-full text-sm">
          <TableHead className="text-gray-400">
            <TableRow>
              <TableHeaderCell>Atendimento</TableHeaderCell>
              <TableHeaderCell>SIGTAP</TableHeaderCell>
              <TableHeaderCell>CID</TableHeaderCell>
              <TableHeaderCell>Qtd</TableHeaderCell>
              <TableHeaderCell>Status</TableHeaderCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {procedimentos.map((p) => (
              <TableRow key={p.atendimento} className="border-b border-slate-800">
                <TableCell>{p.atendimento}</TableCell>
                <TableCell>{p.sigtap}</TableCell>
                <TableCell>{p.cid}</TableCell>
                <TableCell>{p.quantidade}</TableCell>
                <TableCell>
                  <Badge variant={p.status === "validado" ? "success" : "warning"}>{p.status}</Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Historico de exportacoes</h2>
        <div className="space-y-2">
          <h3 className="text-lg font-semibold">BPA</h3>
          {renderTable(exportsBpa, "bpa")}
        </div>
        <div className="space-y-2">
          <h3 className="text-lg font-semibold">APAC</h3>
          {renderTable(exportsApac, "apac")}
        </div>
      </div>

      {showErrors && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <div className="w-full max-w-lg space-y-3 rounded-lg border border-slate-800 bg-slate-900 p-4">
            <div className="flex items-center justify-between">
              <h4 className="text-lg font-semibold">Erros da exportacao</h4>
              <Button variant="outline" onClick={() => setShowErrors(null)}>
                Fechar
              </Button>
            </div>
            <pre className="max-h-80 overflow-auto rounded bg-slate-950 p-3 text-xs text-slate-100">{JSON.stringify(showErrors, null, 2)}</pre>
          </div>
        </div>
      )}

      {showAssistant && (
        <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md border-l border-slate-800 bg-slate-900 p-4 shadow-xl">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-lg font-semibold">Assistente Clinico</h3>
            <Button variant="outline" onClick={() => setShowAssistant(false)}>
              Fechar
            </Button>
          </div>
          <AssistantChat />
        </div>
      )}
    </main>
  );
}
