"use client";
import { resetUserPassword, updateUser } from "../../lib/api";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeaderCell, TableRow } from "../ui/table";
import { useNotifications } from "../ui/notifications";

type Props = {
  users: { id: number; nome: string; email: string; roles: string[]; ativo: boolean; must_change_password: boolean }[];
  onRefresh: () => void;
};

export function UserTable({ users, onRefresh }: Props) {
  const { notifySuccess, notifyError } = useNotifications();

  async function handleReset(id: number) {
    try {
      await resetUserPassword(id, {});
      notifySuccess("Senha resetada");
      onRefresh();
    } catch (err: any) {
      notifyError(err?.message || "Erro ao resetar senha");
    }
  }

  async function toggleActive(id: number, ativo: boolean) {
    try {
      await updateUser(id, { is_active: !ativo });
      notifySuccess(!ativo ? "Usuário ativado" : "Usuário desativado");
      onRefresh();
    } catch (err: any) {
      notifyError(err?.message || "Erro ao atualizar usuário");
    }
  }

  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableHeaderCell>Nome</TableHeaderCell>
          <TableHeaderCell>Email</TableHeaderCell>
          <TableHeaderCell>Roles</TableHeaderCell>
          <TableHeaderCell>Ativo</TableHeaderCell>
          <TableHeaderCell>Must Change Password</TableHeaderCell>
          <TableHeaderCell className="text-center">Ações</TableHeaderCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {users.map((u) => (
          <TableRow key={u.id}>
            <TableCell>{u.nome}</TableCell>
            <TableCell>{u.email}</TableCell>
            <TableCell className="space-x-1">
              {u.roles.map((role) => (
                <Badge key={role}>{role}</Badge>
              ))}
            </TableCell>
            <TableCell>
              <Badge variant={u.ativo ? "success" : "danger"}>{u.ativo ? "Sim" : "Não"}</Badge>
            </TableCell>
            <TableCell>
              <Badge variant={u.must_change_password ? "warning" : "default"}>
                {u.must_change_password ? "Sim" : "Não"}
              </Badge>
            </TableCell>
            <TableCell className="space-x-2 text-right">
              <Button variant="outline" onClick={() => handleReset(u.id)}>
                Reset senha
              </Button>
              <Button variant="secondary" onClick={() => toggleActive(u.id, u.ativo)}>
                {u.ativo ? "Desativar" : "Ativar"}
              </Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
