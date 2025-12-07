"use client";

import { useEffect, useMemo, useState } from "react";
import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";

import { AssistantChat } from "../../components/clinical/AssistantChat";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { useNotifications } from "../../components/ui/notifications";
import { createEvolucao, getAtendimentos, getEvolucoes } from "../../lib/api";
import { getSession } from "../../lib/auth";

export default function ProntuarioPage() {
  const { notifyError, notifySuccess } = useNotifications();
  const [atendimentos, setAtendimentos] = useState<any[]>([]);
  const [evolucoes, setEvolucoes] = useState<any[]>([]);
  const [selectedAtendimento, setSelectedAtendimento] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [showAssistant, setShowAssistant] = useState(false);
  const editor = useEditor({ extensions: [StarterKit], content: "<p>Registrar evolução clínica...</p>" });

  useEffect(() => {
    async function loadAtendimentos() {
      try {
        const ats = await getAtendimentos();
        setAtendimentos(ats);
        if (ats.length) setSelectedAtendimento(ats[0].id);
      } catch (err: any) {
        notifyError(err?.message || "Erro ao carregar atendimentos");
      } finally {
        setLoading(false);
      }
    }
    loadAtendimentos();
  }, [notifyError]);

  useEffect(() => {
    async function loadEvolucoes() {
      try {
        const all = await getEvolucoes();
        setEvolucoes(all);
      } catch (err: any) {
        notifyError(err?.message || "Erro ao carregar evoluções");
      }
    }
    loadEvolucoes();
  }, [notifyError]);

  const evolucoesSelecionadas = useMemo(
    () => evolucoes.filter((e) => e.atendimento_id === selectedAtendimento),
    [evolucoes, selectedAtendimento],
  );

  async function handleSalvar() {
    if (!selectedAtendimento || !editor) return;
    const session = getSession();
    try {
      await createEvolucao({
        tenant_id: session?.tenantId,
        atendimento_id: selectedAtendimento,
        texto_estruturado: editor.getHTML(),
        assinado: false,
        assinatura_meta: {},
      });
      notifySuccess("Evolução salva");
      const all = await getEvolucoes();
      setEvolucoes(all);
    } catch (err: any) {
      notifyError(err?.message || "Erro ao salvar evolução");
    }
  }

  const selectedText = editor?.state.doc.textBetween(0, editor.state.doc.content.size, " ");

  return (
    <main className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Prontuário eletrônico</h1>
        <div className="flex items-center gap-2">
          <label className="text-sm text-slate-300">Atendimento</label>
          <select
            className="rounded border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
            value={selectedAtendimento ?? ""}
            onChange={(e) => setSelectedAtendimento(Number(e.target.value))}
          >
            {atendimentos.map((at) => (
              <option key={at.id} value={at.id}>
                #{at.id} - {new Date(at.data).toLocaleString("pt-BR")}
              </option>
            ))}
          </select>
          <Button variant="secondary" onClick={() => setShowAssistant((v) => !v)}>
            Assistente Clínico
          </Button>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-3 rounded-lg border border-slate-800 bg-slate-900/60 p-4">
          <div className="flex flex-wrap gap-2 text-sm">
            <Button variant="secondary" onClick={() => editor?.chain().focus().toggleBold().run()}>
              Negrito
            </Button>
            <Button variant="secondary" onClick={() => editor?.chain().focus().toggleItalic().run()}>
              Itálico
            </Button>
            <Button variant="secondary" onClick={() => editor?.chain().focus().toggleBulletList().run()}>
              Lista
            </Button>
            <Button variant="secondary" onClick={() => editor?.chain().focus().toggleHeading({ level: 2 }).run()}>
              Título
            </Button>
          </div>
          <div className="min-h-[240px] rounded border border-slate-800 bg-slate-950 p-3">
            <EditorContent editor={editor} />
          </div>
          <Button onClick={handleSalvar} disabled={!selectedAtendimento || loading}>
            Salvar evolução
          </Button>
        </div>

        <div className="space-y-3 rounded-lg border border-slate-800 bg-slate-900/60 p-4">
          <h2 className="text-lg font-semibold">Histórico</h2>
          {evolucoesSelecionadas.length === 0 && <p className="text-sm text-slate-400">Nenhuma evolução ainda.</p>}
          <div className="max-h-[420px] space-y-3 overflow-auto">
            {evolucoesSelecionadas.map((ev) => (
              <div key={ev.id} className="rounded border border-slate-800 bg-slate-950 p-3 text-sm">
                <div className="mb-1 flex items-center justify-between text-xs text-slate-400">
                  <span>{new Date(ev.criado_em || ev.data || Date.now()).toLocaleString("pt-BR")}</span>
                  <Badge variant={ev.assinado ? "success" : "default"}>{ev.assinado ? "Assinado" : "Rascunho"}</Badge>
                </div>
                <div
                  className="prose prose-invert max-w-none text-sm"
                  dangerouslySetInnerHTML={{ __html: ev.texto_estruturado }}
                />
              </div>
            ))}
          </div>
        </div>
      </div>

      {showAssistant && (
        <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md border-l border-slate-800 bg-slate-900 p-4 shadow-xl">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-lg font-semibold">Assistente Clínico</h3>
            <Button variant="outline" onClick={() => setShowAssistant(false)}>
              Fechar
            </Button>
          </div>
          <AssistantChat initialContext={selectedText || ""} />
        </div>
      )}
    </main>
  );
}
