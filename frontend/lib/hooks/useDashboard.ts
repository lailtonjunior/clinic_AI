"use client";

import { useQuery } from "@tanstack/react-query";
import { apiGet } from "../api/client";
import type { DashboardResponse } from "../api/types";

export function useDashboard() {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: () => apiGet<DashboardResponse>("/api/core/dashboard"),
    staleTime: 30 * 1000, // 30 seconds
  });
}
