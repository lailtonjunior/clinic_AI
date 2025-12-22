"use client";

import { useMutation } from "@tanstack/react-query";
import { apiPost } from "../api/client";
import type { AssistantReply } from "../api/types";

export function useAskAssistant() {
  return useMutation({
    mutationFn: async (payload: {
      mensagem: string;
      paciente_id?: number;
      atendimento_id?: number;
    }) => {
      return apiPost<AssistantReply>("/api/ai/assistente", payload);
    },
  });
}

