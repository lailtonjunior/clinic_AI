import "./globals.css";
import { ReactNode } from "react";
import { AppShell } from "../components/AppShell";
import { Providers } from "../lib/providers";

export const metadata = {
  title: "NexusClin",
  description: "PEP + Gestao Clinica + BPA/APAC",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>
        <Providers>
          <AppShell>{children}</AppShell>
        </Providers>
      </body>
    </html>
  );
}
