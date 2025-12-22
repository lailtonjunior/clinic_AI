"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiGet, apiPut } from "../api/client";
import type { AgendaItem } from "../api/types";

export function useAgendas() {
  return useQuery({
    queryKey: ["agendas"],
    queryFn: () => apiGet<AgendaItem[]>("/api/agendas"),
    staleTime: 30 * 1000,
  });
}

export function useUpdateAgenda() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: Partial<AgendaItem> }) => {
      return apiPut<AgendaItem>(`/api/agendas/${id}`, payload);
    },
    onMutate: async ({ id, payload }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ["agendas"] });

      // Snapshot previous value
      const previousAgendas = queryClient.getQueryData<AgendaItem[]>(["agendas"]);

      // Optimistically update
      queryClient.setQueryData<AgendaItem[]>(["agendas"], (old) => {
        if (!old) return old;
        return old.map((item) => (item.id === id ? { ...item, ...payload } : item));
      });

      return { previousAgendas };
    },
    onError: (_err, _variables, context) => {
      // Rollback on error
      if (context?.previousAgendas) {
        queryClient.setQueryData(["agendas"], context.previousAgendas);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agendas"] });
    },
  });
}

