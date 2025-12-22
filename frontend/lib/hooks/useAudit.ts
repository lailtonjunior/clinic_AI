"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { apiGet, apiPost } from "../api/client";
import type { AuditResponse } from "../api/types";

export function useAudit(competencia: string, enabled = true) {
  return useQuery({
    queryKey: ["audit", competencia],
    queryFn: () => apiGet<AuditResponse>(`/api/audit/competencia/${competencia}`),
    enabled: enabled && /^\d{6}$/.test(competencia),
    staleTime: 60 * 1000, // 1 minute
  });
}

export function usePostBpa() {
  return useMutation({
    mutationFn: async (competencia: string) => {
      return apiPost<{ url: string; preview: string }>(`/api/exports/bpa?competencia=${competencia}`);
    },
  });
}

export function usePostApac() {
  return useMutation({
    mutationFn: async (competencia: string) => {
      return apiPost<{ url: string; preview: string }>(`/api/exports/apac?competencia=${competencia}`);
    },
  });
}
