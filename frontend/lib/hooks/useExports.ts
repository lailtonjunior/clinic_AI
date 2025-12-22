"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiGet, apiPost } from "../api/client";
import type { ExportItem } from "../api/types";

export function useExports(tipo: "bpa" | "apac", competencia?: string) {
  return useQuery({
    queryKey: ["exports", tipo, competencia],
    queryFn: () => {
      const params = competencia ? `?tipo=${tipo}&competencia=${competencia}` : `?tipo=${tipo}`;
      return apiGet<ExportItem[]>(`/api/exports${params}`);
    },
    staleTime: 30 * 1000,
  });
}

export function useRetryExport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ tipo, id }: { tipo: "bpa" | "apac"; id: number }) => {
      return apiPost(`/api/exports/${tipo}/${id}/retry`);
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["exports", variables.tipo] });
    },
  });
}

