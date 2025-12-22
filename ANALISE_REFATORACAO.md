# 📊 Análise do Estado da Refatoração - NexusClin

**Data da Análise:** 2025-01-XX  
**Fase Atual:** FASE 1 - FRONTEND CORE & PERFORMANCE

---

## ✅ IMPLEMENTADO COMPLETAMENTE

### 1. **Infraestrutura Base**
- ✅ **TanStack Query Provider** configurado no `layout.tsx`
- ✅ **Cliente HTTP Base** (`lib/api/client.ts`) com:
  - Tratamento de erros padronizado (`ApiError`)
  - Interceptor de autenticação automático
  - Suporte para JSON e texto
- ✅ **Types Centralizados** (`lib/api/types.ts`) com todas as interfaces TypeScript

### 2. **Middleware de Autenticação**
- ✅ **`middleware.ts`** criado na raiz do frontend
  - Proteção de rotas antes da renderização
  - Verificação de cookie `nexusclin_token`
  - Redirecionamento automático para `/login` se não autenticado
  - Redirecionamento de `/login` para `/dashboard` se já autenticado

### 3. **Hooks Modulares com TanStack Query**
Todos os hooks criados em `lib/hooks/`:
- ✅ `useAuth.ts` - Login, Logout, ChangePassword, Session
- ✅ `useDashboard.ts` - Dashboard data
- ✅ `useAudit.ts` - Auditoria, PostBpa, PostApac
- ✅ `useUsers.ts` - CRUD completo de usuários
- ✅ `useTenants.ts` - CRUD completo de tenants
- ✅ `useExports.ts` - Listagem e retry de exports
- ✅ `useAgenda.ts` - Listagem e update com optimistic updates
- ✅ `useEvolucoes.ts` - Listagem e criação
- ✅ `useAtendimentos.ts` - Listagem
- ✅ `useAssistant.ts` - Chat com assistente

### 4. **Componentes Refatorados**
- ✅ **`AppShell.tsx`** - Removida lógica de autenticação client-side, agora usa `useSession()`
- ✅ **`app/login/page.tsx`** - Migrado para `useLogin()` hook
- ✅ **`app/auditoria/page.tsx`** - Migrado para hooks `useAudit`, `usePostBpa`, `usePostApac`
- ✅ **`app/agenda/page.tsx`** - Migrado para `useAgendas()` e `useUpdateAgenda()` com optimistic updates

---

## ⚠️ PARCIALMENTE IMPLEMENTADO

### 1. **Páginas que AINDA usam `lib/api.ts` (antigo)**
Precisam ser migradas para hooks:

#### 🔴 **CRÍTICO - Páginas Principais:**
- ⚠️ `app/producao/page.tsx`
  - Usa: `getExports`, `retryExport`, `ExportItem`
  - Deveria usar: `useExports()`, `useRetryExport()`
  - Status: **50%** - Estrutura pronta, falta migrar chamadas de API

- ⚠️ `app/prontuario/page.tsx`
  - Usa: `getAtendimentos`, `getEvolucoes`, `createEvolucao`, `Atendimento`, `Evolucao`
  - Deveria usar: `useAtendimentos()`, `useEvolucoes()`, `useCreateEvolucao()`
  - Status: **40%** - Hooks criados, página ainda usa API antiga

- ⚠️ `app/perfil/page.tsx`
  - Usa: `changePassword`
  - Deveria usar: `useChangePassword()` do `useAuth`
  - Status: **30%** - Hook existe, página não migrada

#### 🟡 **MÉDIO - Páginas de Configuração:**
- ⚠️ `app/config/usuarios/page.tsx`
  - Usa: `getUsers`, `createUser`, `User`
  - Deveria usar: `useUsers()`, `useCreateUser()`
  - Status: **30%** - Hooks prontos, página e componentes não migrados

- ⚠️ `app/config/tenants/page.tsx`
  - Usa: `getTenants`, `createTenant`, `Tenant`
  - Deveria usar: `useTenants()`, `useCreateTenant()`
  - Status: **30%** - Hooks prontos, página não migrada

#### 🟢 **Componentes que precisam migração:**
- ⚠️ `components/users/UserForm.tsx` - Usa `createUser` (antigo)
- ⚠️ `components/users/UserTable.tsx` - Usa `updateUser`, `resetUserPassword` (antigos)
- ⚠️ `components/tenants/TenantTable.tsx` - Usa `updateTenant` (antigo)
- ⚠️ `components/clinical/AssistantChat.tsx` - Usa `askAssistant` (antigo)

### 2. **TypeScript Strict Mode**
- ⚠️ `tsconfig.json` ainda tem `"strict": false`
- ⚠️ Deveria estar em modo strict para melhor type safety
- Status: **0%** - Não implementado

### 3. **Dashboard Page**
- ⚠️ `app/dashboard/page.tsx` está com dados **mockados/hardcoded**
- ⚠️ Deveria usar `useDashboard()` hook para buscar dados reais
- Status: **20%** - Hook existe, página usa dados estáticos

---

## ❌ NÃO IMPLEMENTADO

### 1. **Remoção do `lib/api.ts`**
- ❌ Arquivo ainda existe e está sendo importado em **8+ lugares**
- ❌ Bloqueia conclusão da refatoração
- ❌ **PRIORIDADE ALTA**

### 2. **Skeleton Screens / Loading States**
- ❌ Ainda não há skeletons para estados de carregamento
- ❌ Apenas spinners genéricos ou texto "Carregando..."
- ❌ Deveria ter: `<DashboardSkeleton />`, `<TableSkeleton />`, etc.

### 3. **Error Boundaries**
- ❌ Não há tratamento de erros global com Error Boundaries
- ❌ Erros do TanStack Query podem quebrar a UI
- ❌ Deveria ter: `<ErrorBoundary>` component

### 4. **Otimistic Updates (Adicional)**
- ✅ `useUpdateAgenda` já tem optimistic updates
- ❌ Outras mutações não têm (ex: `useUpdateUser`, `useCreateUser`)
- ❌ Poderia melhorar UX significativamente

### 5. **Validação com Zod**
- ❌ Formulários não usam `zod` para validação schema-first
- ❌ `react-hook-form` não está sendo utilizado
- ❌ Dependências instaladas mas não usadas

### 6. **Server Components (RSC)**
- ❌ Todas as páginas são `"use client"`
- ❌ Não há uso de React Server Components
- ❌ Dashboard poderia ser Server Component com dados do servidor

---

## 🔍 PROBLEMAS IDENTIFICADOS

### 1. **Inconsistência de Imports**
- ❌ Alguns arquivos importam de `lib/api.ts` (antigo)
- ❌ Outros importam de `lib/api/types.ts` + hooks
- ❌ Isso causa confusão e impede remoção do `api.ts`

### 2. **Tipos Duplicados**
- ⚠️ Types podem estar duplicados entre `lib/api.ts` e `lib/api/types.ts`
- ⚠️ Precisa verificar e consolidar

### 3. **Middleware Cookie Sync**
- ⚠️ Middleware verifica cookie `nexusclin_token`
- ⚠️ `auth.ts` salva em localStorage E cookie (duplicação)
- ⚠️ Funciona, mas poderia ser otimizado (só cookie)

### 4. **Error Handling Inconsistente**
- ⚠️ Alguns lugares usam `try/catch` com `notifyError`
- ⚠️ Outros confiam no TanStack Query error handling
- ⚠️ Falta padronização

### 5. **Loading States Inconsistentes**
- ⚠️ Alguns componentes usam `isLoading` do TanStack Query
- ⚠️ Outros mantêm `loading` state local
- ⚠️ Mistura causa inconsistência na UI

---

## 📋 PLANO DE AÇÃO RECOMENDADO

### **FASE 1.1: Completar Migração das Páginas** (Prioridade ALTA)

1. **Migrar páginas principais:**
   - [ ] `app/producao/page.tsx` → usar `useExports()`, `useRetryExport()`
   - [ ] `app/prontuario/page.tsx` → usar `useAtendimentos()`, `useEvolucoes()`, `useCreateEvolucao()`
   - [ ] `app/perfil/page.tsx` → usar `useChangePassword()`
   - [ ] `app/dashboard/page.tsx` → usar `useDashboard()` (remover dados mockados)

2. **Migrar páginas de configuração:**
   - [ ] `app/config/usuarios/page.tsx` → usar `useUsers()`, `useCreateUser()`
   - [ ] `app/config/tenants/page.tsx` → usar `useTenants()`, `useCreateTenant()`

3. **Migrar componentes:**
   - [ ] `components/users/UserForm.tsx` → usar `useCreateUser()`
   - [ ] `components/users/UserTable.tsx` → usar `useUpdateUser()`, `useResetUserPassword()`
   - [ ] `components/tenants/TenantTable.tsx` → usar `useUpdateTenant()`
   - [ ] `components/clinical/AssistantChat.tsx` → usar `useAskAssistant()`

### **FASE 1.2: Limpeza e Finalização** (Prioridade ALTA)

4. **Remover `lib/api.ts`:**
   - [ ] Verificar se todos os imports foram migrados
   - [ ] Deletar `frontend/lib/api.ts`
   - [ ] Verificar se não há quebras

5. **TypeScript Strict Mode:**
   - [ ] Habilitar `"strict": true` no `tsconfig.json`
   - [ ] Corrigir erros de tipo que surgirem
   - [ ] Adicionar tipos faltantes

### **FASE 1.3: Melhorias de UX** (Prioridade MÉDIA)

6. **Skeleton Screens:**
   - [ ] Criar componentes de skeleton reutilizáveis
   - [ ] Aplicar em páginas principais (Dashboard, Agenda, etc.)
   - [ ] Substituir "Carregando..." por skeletons

7. **Error Boundaries:**
   - [ ] Criar `<ErrorBoundary>` component
   - [ ] Envolver páginas principais
   - [ ] Melhorar mensagens de erro

8. **Otimistic Updates Adicionais:**
   - [ ] Adicionar optimistic updates em `useUpdateUser`
   - [ ] Adicionar optimistic updates em `useCreateUser`
   - [ ] Melhorar feedback visual

### **FASE 2: Validação e Formulários** (Prioridade MÉDIA)

9. **Zod + React Hook Form:**
   - [ ] Criar schemas Zod para formulários principais
   - [ ] Migrar formulários para `react-hook-form`
   - [ ] Validar no client-side e server-side

### **FASE 3: Server Components** (Prioridade BAIXA)

10. **React Server Components:**
    - [ ] Identificar páginas que podem ser Server Components
    - [ ] Migrar Dashboard para Server Component (se possível)
    - [ ] Otimizar bundle size

---

## 📊 MÉTRICAS DE PROGRESSO

### **Completude Geral da FASE 1: ~60%**

| Categoria | Progresso | Status |
|-----------|-----------|--------|
| Infraestrutura Base | 100% | ✅ Completo |
| Middleware Auth | 100% | ✅ Completo |
| Hooks Modulares | 100% | ✅ Completo |
| Migração de Páginas | 40% | ⚠️ Parcial |
| Migração de Componentes | 25% | ⚠️ Parcial |
| Remoção `api.ts` | 0% | ❌ Pendente |
| TypeScript Strict | 0% | ❌ Pendente |
| Skeleton Screens | 0% | ❌ Pendente |
| Error Boundaries | 0% | ❌ Pendente |

### **Arquivos que Precisam de Atenção (10 arquivos):**

1. ❌ `frontend/lib/api.ts` - **DELETAR** (depois da migração)
2. ⚠️ `frontend/app/producao/page.tsx` - Migrar para hooks
3. ⚠️ `frontend/app/prontuario/page.tsx` - Migrar para hooks
4. ⚠️ `frontend/app/perfil/page.tsx` - Migrar para hooks
5. ⚠️ `frontend/app/dashboard/page.tsx` - Usar dados reais
6. ⚠️ `frontend/app/config/usuarios/page.tsx` - Migrar para hooks
7. ⚠️ `frontend/app/config/tenants/page.tsx` - Migrar para hooks
8. ⚠️ `frontend/components/users/UserForm.tsx` - Migrar para hooks
9. ⚠️ `frontend/components/users/UserTable.tsx` - Migrar para hooks
10. ⚠️ `frontend/components/tenants/TenantTable.tsx` - Migrar para hooks
11. ⚠️ `frontend/components/clinical/AssistantChat.tsx` - Migrar para hooks
12. ⚠️ `frontend/tsconfig.json` - Habilitar strict mode

---

## 🎯 CONCLUSÃO

A refatoração está **bem encaminhada**, com a infraestrutura base completa. O maior bloqueio atual é a **migração das páginas e componentes** que ainda usam o `lib/api.ts` antigo.

**Próximos Passos Imediatos:**
1. Completar migração das páginas restantes (2-3 horas de trabalho)
2. Remover `lib/api.ts` após verificação completa
3. Habilitar TypeScript strict mode e corrigir tipos
4. Adicionar skeleton screens para melhorar UX

**Estimativa para completar FASE 1:** ~4-6 horas de trabalho focado.

