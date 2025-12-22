"use client";

import { useQuery } from "@tanstack/react-query";
import { apiGet } from "../api/client";
import type { Atendimento } from "../api/types";

export function useAtendimentos() {
  return useQuery({
    queryKey: ["atendimentos"],
    queryFn: () => apiGet<Atendimento[]>("/api/atendimentos"),
    staleTime: 30 * 1000,
  });
}

