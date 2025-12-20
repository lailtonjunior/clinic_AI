"use client";
import { Suspense, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { CompetenciaPicker } from "../../components/sus/CompetenciaPicker";
import { AuditoriaResultado } from "../../components/sus/AuditoriaResultado";
import { getAudit, postApac, postBpa, fetchRemFile, AuditError } from "../../lib/api";

type AuditStatus = "pending" | "ok" | "error";

export default function AuditoriaPage() {
  return (
    <Suspense fallback={<div className="text-slate-400">Carregando auditoria...</div>}>
      <AuditoriaContent />
    </Suspense>
  );
}

function AuditoriaContent() {
  const searchParams = useSearchParams();
  const initialCompetencia = searchParams.get("competencia") || "202501";

  const [competencia, setCompetencia] = useState(initialCompetencia);
  const [auditStatus, setAuditStatus] = useState<AuditStatus>("pending");
  const [erros, setErros] = useState<AuditError[]>([]);
  const [preview, setPreview] = useState("");
  const [downloadUrlBpa, setDownloadUrlBpa] = useState<string | null>(null);
  const [downloadUrlApac, setDownloadUrlApac] = useState<string | null>(null);
  const [loadingAudit, setLoadingAudit] = useState(false);
  const [loadingBpa, setLoadingBpa] = useState(false);
  const [loadingApac, setLoadingApac] = useState(false);
  const competenciaValida = useMemo(() => /^\d{6}$/.test(competencia), [competencia]);

  useEffect(() => {
    if (competenciaValida) {
      runAudit(competencia);
    }
  }, [competenciaValida]);

  async function runAudit(cmp: string) {
    if (!/^\d{6}$/.test(cmp)) return;
    setLoadingAudit(true);
    setAuditStatus("pending");
    try {
      const data = await getAudit(cmp);
      const errs = data.erros || [];
      setErros(errs);
      setAuditStatus(errs.length === 0 ? "ok" : "error");
    } catch (err) {
      console.error(err);
      setAuditStatus("error");
    } finally {
      setLoadingAudit(false);
    }
  }

  async function handleExport(
    tipo: "bpa" | "apac",
    setUrl: (url: string | null) => void,
    setLoading: (v: boolean) => void,
  ) {
    if (!competenciaValida) return;
    setLoading(true);
    setPreview("");
    try {
      const { url, preview } = tipo === "bpa" ? await postBpa(competencia) : await postApac(competencia);
      let conteudo = preview;
      try {
        conteudo = await fetchRemFile(url);
      } catch {
        // fallback para preview parcial
      }
      const blob = new Blob([conteudo], { type: "text/plain" });
      const blobUrl = URL.createObjectURL(blob);
      setUrl(blobUrl);
      setPreview(conteudo.slice(0, 800));
    } catch (err) {
      console.error(err);
      setUrl(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <h1 className="text-2xl">Auditoria & Exportação</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="card lg:col-span-1 space-y-3">
          <CompetenciaPicker value={competencia} onChange={setCompetencia} disabled={loadingAudit} />
          <button
            className="px-4 py-2 bg-sky-600 rounded text-sm disabled:opacity-50"
            onClick={() => runAudit(competencia)}
            disabled={!competenciaValida || loadingAudit}
          >
            {loadingAudit ? "Auditando..." : "Rodar auditoria"}
          </button>
          <AuditoriaResultado status={auditStatus} erros={erros} />
        </div>

        <div className="card lg:col-span-2 space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            <button
              className="px-4 py-2 bg-sky-500 rounded text-sm disabled:opacity-50"
              onClick={() => handleExport("bpa", setDownloadUrlBpa, setLoadingBpa)}
              disabled={auditStatus !== "ok" || loadingAudit || loadingBpa}
            >
              {loadingBpa ? "Gerando BPA..." : "Gerar BPA-I"}
            </button>
            <button
              className="px-4 py-2 bg-sky-700 rounded text-sm disabled:opacity-50"
              onClick={() => handleExport("apac", setDownloadUrlApac, setLoadingApac)}
              disabled={auditStatus !== "ok" || loadingAudit || loadingApac}
            >
              {loadingApac ? "Gerando APAC..." : "Gerar APAC"}
            </button>
            {downloadUrlBpa && (
              <a
                href={downloadUrlBpa}
                download={`BPA_${competencia}.rem`}
                className="text-sm text-sky-300 underline"
              >
                Download BPA
              </a>
            )}
            {downloadUrlApac && (
              <a
                href={downloadUrlApac}
                download={`APAC_${competencia}.rem`}
                className="text-sm text-sky-300 underline"
              >
                Download APAC
              </a>
            )}
          </div>

          <div className="space-y-2">
            <div className="text-sm text-slate-400">Preview arquivo .rem (primeiras linhas)</div>
            <textarea
              className="w-full h-64 bg-slate-900 border border-slate-800 rounded p-2 text-xs"
              value={preview}
              readOnly
            />
          </div>
        </div>
      </div>
    </main>
  );
}
