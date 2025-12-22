# Fix: PowerShell Execution Policy Error

## Problema

Ao tentar executar `npm install` no PowerShell, você pode encontrar este erro:

```
npm : O arquivo C:\Program Files\nodejs\npm.ps1 não pode ser carregado porque a execução de scripts foi desabilitada neste sistema.
```

## Solução Temporária (Para esta sessão)

Execute no PowerShell:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

Isso altera a política apenas para o processo atual (terminal) e é revertido quando você fecha o terminal.

## Solução Permanente (Recomendada)

Para alterar permanentemente para o usuário atual:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**O que isso faz:**
- `RemoteSigned`: Permite scripts locais e scripts baixados da internet se forem assinados por um editor confiável
- `CurrentUser`: Aplica apenas ao usuário atual, não requer privilégios de administrador

## Alternativa: Usar CMD

Se preferir não alterar a política do PowerShell, você pode usar o **Command Prompt (cmd)** ao invés do PowerShell:

```cmd
cd frontend
npm install
```

## Verificar Política Atual

Para ver a política atual:

```powershell
Get-ExecutionPolicy -List
```

## Segurança

A política `RemoteSigned` é segura porque:
- ✅ Permite executar scripts locais (como npm)
- ✅ Bloqueia scripts baixados da internet que não sejam assinados
- ✅ Não requer privilégios de administrador quando usado com `-Scope CurrentUser`

