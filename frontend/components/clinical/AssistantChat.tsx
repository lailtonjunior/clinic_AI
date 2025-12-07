"use client";

import { useState } from "react";

import { askAssistant } from "../../lib/api";
import { Button } from "../ui/button";
import { useNotifications } from "../ui/notifications";

type Message = { role: "user" | "assistant"; content: string };

type Props = {
  initialContext?: string;
};

export function AssistantChat({ initialContext }: Props) {
  const { notifyError } = useNotifications();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function send() {
    const content = input.trim();
    if (!content) return;
    setLoading(true);
    setMessages((prev) => [...prev, { role: "user", content }]);
    setInput("");
    try {
      const res = await askAssistant({ mensagem: initialContext ? `${initialContext}\n\n${content}` : content });
      setMessages((prev) => [...prev, { role: "assistant", content: res.resposta }]);
    } catch (err: any) {
      notifyError(err?.message || "Erro ao consultar assistente");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-full flex-col gap-3">
      <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3 text-xs text-slate-300">
        <strong>Aviso:</strong> Assistente clínico de apoio. Não substitui decisão profissional.
      </div>
      <div className="flex-1 space-y-2 overflow-auto rounded-lg border border-slate-800 bg-slate-950 p-3">
        {messages.length === 0 && <p className="text-sm text-slate-500">Envie uma mensagem para começar.</p>}
        {messages.map((msg, idx) => (
          <div key={idx} className={msg.role === "assistant" ? "text-sky-200" : "text-slate-200"}>
            <span className="mr-1 text-xs uppercase text-slate-500">
              {msg.role === "assistant" ? "Assistente:" : "Você:"}
            </span>
            {msg.content}
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          className="flex-1 rounded border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-1 focus:ring-sky-500"
          placeholder="Pergunte sobre CID, procedimentos, sugestões..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              send();
            }
          }}
        />
        <Button onClick={send} disabled={loading}>
          {loading ? "Enviando..." : "Enviar"}
        </Button>
      </div>
    </div>
  );
}
