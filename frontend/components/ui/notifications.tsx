"use client";

import { createContext, ReactNode, useCallback, useContext, useMemo, useState } from "react";

type ToastType = "success" | "error";

type Toast = {
  id: string;
  message: string;
  type: ToastType;
  timeout?: number;
};

type NotificationsContextType = {
  notifySuccess: (message: string, timeout?: number) => void;
  notifyError: (message: string, timeout?: number) => void;
};

const NotificationsContext = createContext<NotificationsContextType | undefined>(undefined);

function cx(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

export function NotificationsProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const remove = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const push = useCallback(
    (message: string, type: ToastType, timeout = 4000) => {
      const id =
        typeof crypto !== "undefined" && crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`;
      setToasts((prev) => [...prev, { id, message, type, timeout }]);
      if (timeout > 0) {
        setTimeout(() => remove(id), timeout);
      }
    },
    [remove],
  );

  const value = useMemo(
    () => ({
      notifySuccess: (message: string, timeout?: number) => push(message, "success", timeout),
      notifyError: (message: string, timeout?: number) => push(message, "error", timeout),
    }),
    [push],
  );

  return (
    <NotificationsContext.Provider value={value}>
      {children}
      <div className="fixed right-4 top-4 z-50 flex max-w-sm flex-col gap-3">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={cx(
              "rounded-lg border px-4 py-3 text-sm shadow-lg",
              toast.type === "success"
                ? "border-emerald-700 bg-emerald-900/80 text-emerald-50"
                : "border-rose-700 bg-rose-900/80 text-rose-50",
            )}
            role="status"
          >
            {toast.message}
          </div>
        ))}
      </div>
    </NotificationsContext.Provider>
  );
}

export function useNotifications(): NotificationsContextType {
  const ctx = useContext(NotificationsContext);
  if (!ctx) {
    throw new Error("useNotifications must be used within NotificationsProvider");
  }
  return ctx;
}
