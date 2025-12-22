"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiGet, apiPost, apiPut } from "../api/client";
import type { Tenant } from "../api/types";

export function useTenants() {
  return useQuery({
    queryKey: ["tenants"],
    queryFn: () => apiGet<Tenant[]>("/api/tenants"),
    staleTime: 60 * 1000,
  });
}

export function useCreateTenant() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: { name: string; cnpj?: string }) => {
      return apiPost<Tenant>("/api/tenants", payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tenants"] });
    },
  });
}

export function useUpdateTenant() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: Partial<Tenant> }) => {
      return apiPut<Tenant>(`/api/tenants/${id}`, payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tenants"] });
    },
  });
}

