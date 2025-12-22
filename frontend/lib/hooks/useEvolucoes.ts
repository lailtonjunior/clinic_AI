"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiGet, apiPost } from "../api/client";
import type { Evolucao } from "../api/types";

export function useEvolucoes() {
  return useQuery({
    queryKey: ["evolucoes"],
    queryFn: () => apiGet<Evolucao[]>("/api/evolucoes"),
    staleTime: 30 * 1000,
  });
}

export function useCreateEvolucao() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: {
      atendimento_id: number;
      texto_estruturado?: string;
      [key: string]: unknown;
    }) => {
      return apiPost<Evolucao>("/api/evolucoes", payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["evolucoes"] });
    },
  });
}

