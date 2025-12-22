"use client";
import { Suspense, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { CompetenciaPicker } from "../../components/sus/CompetenciaPicker";
import { AuditoriaResultado } from "../../components/sus/AuditoriaResultado";
import { useAudit, usePostBpa, usePostApac } from "../../lib/hooks/useAudit";
import { apiGet } from "../../lib/api/client";
import type { AuditError } from "../../lib/api/types";

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
  const [preview, setPreview] = useState("");
  const [downloadUrlBpa, setDownloadUrlBpa] = useState<string | null>(null);
  const [downloadUrlApac, setDownloadUrlApac] = useState<string | null>(null);
  const competenciaValida = useMemo(() => /^\d{6}$/.test(competencia), [competencia]);

  const { data: auditData, isLoading: loadingAudit, refetch: refetchAudit } = useAudit(
    competencia,
    competenciaValida
  );

  const postBpa = usePostBpa();
  const postApac = usePostApac();

  const auditStatus: AuditStatus = loadingAudit
    ? "pending"
    : auditData
      ? auditData.erros.length === 0
        ? "ok"
        : "error"
      : "pending";

  const erros: AuditError[] = auditData?.erros || [];

  async function handleExport(tipo: "bpa" | "apac", setUrl: (url: string | null) => void) {
    if (!competenciaValida) return;
    setPreview("");

    const mutation = tipo === "bpa" ? postBpa : postApac;
    try {
      const result = await mutation.mutateAsync(competencia);
      let conteudo = result.preview;
      try {
        // Try to fetch full file
        const apiBase = process.env.NEXT_PUBLIC_API_URL || "";
        const fullUrl = result.url.startsWith("http") ? result.url : `${apiBase}/${result.url.replace(/^\//, "")}`;
        conteudo = await apiGet<string>(fullUrl);
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
    }
  }

  return (
    <main className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <h1 className="text-2xl">Auditoria & Exportação</h1>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="card space-y-3 lg:col-span-1">
          <CompetenciaPicker value={competencia} onChange={setCompetencia} disabled={loadingAudit} />
          <button
            type="button"
            className="rounded bg-sky-600 px-4 py-2 text-sm disabled:opacity-50"
            onClick={() => refetchAudit()}
            disabled={!competenciaValida || loadingAudit}
          >
            {loadingAudit ? "Auditando..." : "Rodar auditoria"}
          </button>
          <AuditoriaResultado status={auditStatus} erros={erros} />
        </div>

        <div className="card space-y-4 lg:col-span-2">
          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              className="rounded bg-sky-500 px-4 py-2 text-sm disabled:opacity-50"
              onClick={() => handleExport("bpa", setDownloadUrlBpa)}
              disabled={auditStatus !== "ok" || loadingAudit || postBpa.isPending}
            >
              {postBpa.isPending ? "Gerando BPA..." : "Gerar BPA-I"}
            </button>
            <button
              type="button"
              className="rounded bg-sky-700 px-4 py-2 text-sm disabled:opacity-50"
              onClick={() => handleExport("apac", setDownloadUrlApac)}
              disabled={auditStatus !== "ok" || loadingAudit || postApac.isPending}
            >
              {postApac.isPending ? "Gerando APAC..." : "Gerar APAC"}
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
