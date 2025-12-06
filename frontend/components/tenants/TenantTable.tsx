"use client";
import { useState } from "react";
import { updateTenant } from "../../lib/api";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeaderCell, TableRow } from "../ui/table";
import { useNotifications } from "../ui/notifications";

type Tenant = { id: number; name: string; cnpj?: string };

type Props = { tenants: Tenant[]; onRefresh: () => void };

export function TenantTable({ tenants, onRefresh }: Props) {
  const { notifyError, notifySuccess } = useNotifications();
  const [editingId, setEditingId] = useState<number | null>(null);
  const [nameDraft, setNameDraft] = useState("");

  const startEdit = (tenant: Tenant) => {
    setEditingId(tenant.id);
    setNameDraft(tenant.name);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setNameDraft("");
  };

  async function handleSave(id: number) {
    try {
      await updateTenant(id, { name: nameDraft });
      notifySuccess("Tenant atualizado");
      cancelEdit();
      onRefresh();
    } catch (err: any) {
      notifyError(err?.message || "Erro ao atualizar tenant");
    }
  }

  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableHeaderCell>ID</TableHeaderCell>
          <TableHeaderCell>Nome</TableHeaderCell>
          <TableHeaderCell>CNPJ</TableHeaderCell>
          <TableHeaderCell className="text-center">Ações</TableHeaderCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {tenants.map((t) => {
          const isEditing = editingId === t.id;
          return (
            <TableRow key={t.id}>
              <TableCell>{t.id}</TableCell>
              <TableCell>
                {isEditing ? (
                  <Input value={nameDraft} onChange={(e) => setNameDraft(e.target.value)} />
                ) : (
                  t.name
                )}
              </TableCell>
              <TableCell>{t.cnpj || "-"}</TableCell>
              <TableCell className="space-x-2 text-right">
                {isEditing ? (
                  <>
                    <Button variant="secondary" onClick={() => handleSave(t.id)} disabled={!nameDraft.trim()}>
                      Salvar
                    </Button>
                    <Button variant="outline" onClick={cancelEdit}>
                      Cancelar
                    </Button>
                  </>
                ) : (
                  <Button variant="outline" onClick={() => startEdit(t)}>
                    Renomear
                  </Button>
                )}
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}
