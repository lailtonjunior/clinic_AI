"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { apiPost } from "../api/client";
import { clearSession, getSession, saveSession, type Session } from "../auth";
import type { LoginResponse } from "../api/types";

export function useSession() {
  return useQuery({
    queryKey: ["session"],
    queryFn: () => {
      const session = getSession();
      if (!session) {
        throw new Error("Not authenticated");
      }
      return session;
    },
    staleTime: Infinity,
    retry: false,
    refetchOnWindowFocus: false,
  });
}

export function useLogin() {
  const router = useRouter();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: { email: string; password: string; tenant_id: number; mfa_code?: string }) => {
      return apiPost<LoginResponse>("/api/auth/login", payload);
    },
    onSuccess: (data) => {
      const session: Session = {
        token: data.access_token,
        roles: data.roles,
        tenantId: data.tenant_id,
      };
      saveSession(session); // This already sets cookie
      queryClient.setQueryData(["session"], session);
      
      // Redirect based on must_change_password
      if (data.must_change_password) {
        router.push("/perfil");
      } else {
        router.push("/dashboard");
      }
    },
  });
}

export function useLogout() {
  const router = useRouter();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      clearSession(); // This already clears cookie
      queryClient.clear();
    },
    onSuccess: () => {
      router.push("/login");
    },
  });
}

export function useChangePassword() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: { senha_atual: string; senha_nova: string }) => {
      return apiPost("/api/auth/change-password", payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["session"] });
    },
  });
}
