# 🔐 Guia de Login - NexusClin

## Como obter credenciais de acesso

O sistema **não possui credenciais padrão fixas**. Você precisa criar um usuário admin através de uma das opções abaixo:

---

## ✅ Opção 1: Usar Script de Seed (Recomendado)

O sistema possui um script que cria automaticamente um usuário admin baseado em variáveis de ambiente.

### 1. Configure as variáveis no arquivo `.env` do backend:

```env
# Seed de usuário admin inicial
SEED_TENANT_NAME=NexusClin
SEED_ADMIN_EMAIL=admin@nexusclin.com
SEED_ADMIN_PASSWORD=admin123
SEED_RUN_ON_STARTUP=true
```

### 2. Reinicie o backend:

O script roda automaticamente no startup se `SEED_RUN_ON_STARTUP=true`.

### 3. Use as credenciais configuradas:

- **Email:** `admin@nexusclin.com` (ou o valor de `SEED_ADMIN_EMAIL`)
- **Senha:** `admin123` (ou o valor de `SEED_ADMIN_PASSWORD`)
- **Tenant ID:** `1` (geralmente o primeiro tenant criado)

---

## ✅ Opção 2: Executar Script Manualmente

Se você não configurou o seed automático, pode executar manualmente:

### 1. Configure as variáveis de ambiente:

```bash
# Windows PowerShell
$env:SEED_TENANT_NAME="NexusClin"
$env:SEED_ADMIN_EMAIL="admin@nexusclin.com"
$env:SEED_ADMIN_PASSWORD="admin123"

# Linux/Mac
export SEED_TENANT_NAME="NexusClin"
export SEED_ADMIN_EMAIL="admin@nexusclin.com"
export SEED_ADMIN_PASSWORD="admin123"
```

### 2. Execute o script:

```bash
cd backend
python -m app.scripts.seed_initial_admin
```

O script é **idempotente**, então você pode executá-lo várias vezes sem problemas.

---

## ✅ Opção 3: Criar via API (Requer acesso ao banco/API)

Se você já tem acesso ao banco de dados ou pode fazer chamadas diretas à API, pode criar um usuário manualmente.

### Via SQL (PostgreSQL):

```sql
-- 1. Criar tenant (se não existir)
INSERT INTO tenants (name, cnpj) VALUES ('NexusClin', NULL) 
ON CONFLICT DO NOTHING RETURNING id;

-- 2. Obter o ID do tenant (substitua pelo ID retornado)
-- Exemplo: tenant_id = 1

-- 3. Criar usuário (senha: admin123 - hash bcrypt)
INSERT INTO usuarios (email, nome, hashed_password, ativo) 
VALUES (
    'admin@nexusclin.com',
    'Admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYq3Z3x5Y0i', -- hash de "admin123"
    true
) RETURNING id;

-- 4. Atribuir roles ao usuário (substitua user_id e tenant_id pelos IDs reais)
INSERT INTO tenant_user_roles (user_id, tenant_id, role, ativo)
VALUES 
    (1, 1, 'SUPER_ADMIN', true),
    (1, 1, 'ADMIN_TENANT', true);
```

**⚠️ Nota:** O hash acima é apenas um exemplo. Use o script Python para gerar o hash correto da senha.

---

## 🔍 Como descobrir o Tenant ID?

### Opção 1: Via SQL

```sql
SELECT id, name FROM tenants;
```

### Opção 2: Via API (após criar primeiro usuário)

```bash
curl -X GET http://localhost:8000/api/tenants \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

---

## 📝 Credenciais de Teste (Apenas para desenvolvimento)

Se você estiver rodando os testes, eles usam:

- **Email:** `admin@test.com`
- **Senha:** `secret`
- **Tenant ID:** `1` (geralmente)

**⚠️ Essas credenciais só existem no banco de testes, não no banco de produção/desenvolvimento.**

---

## 🚨 Problema: "Credenciais inválidas"

Se você receber erro de credenciais inválidas:

1. **Verifique se o usuário foi criado:**
   ```sql
   SELECT email, ativo FROM usuarios;
   ```

2. **Verifique se o tenant existe:**
   ```sql
   SELECT id, name FROM tenants;
   ```

3. **Verifique se o usuário tem roles atribuídas:**
   ```sql
   SELECT u.email, tur.role, tur.ativo, tur.tenant_id
   FROM usuarios u
   JOIN tenant_user_roles tur ON u.id = tur.user_id
   WHERE u.email = 'admin@nexusclin.com';
   ```

4. **Execute o script de seed novamente:**
   ```bash
   cd backend
   python -m app.scripts.seed_initial_admin
   ```

---

## 🔧 Configuração do Frontend

**Importante:** O frontend precisa de uma variável de ambiente para se conectar ao backend.

Crie o arquivo `frontend/.env.local` com:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Após criar/alterar esse arquivo, reinicie o frontend:

```bash
docker compose -f infra/docker-compose.yml restart frontend
```

**Problema comum:** Se você ver erro 404 ao tentar fazer login, é porque `NEXT_PUBLIC_API_URL` não está configurado.

---

## 🎯 Resumo Rápido

**1. Configure o backend (`.env` do backend):**

```env
SEED_TENANT_NAME=NexusClin
SEED_ADMIN_EMAIL=admin@nexusclin.com
SEED_ADMIN_PASSWORD=admin123
SEED_RUN_ON_STARTUP=true
```

**2. Configure o frontend (`.env.local` do frontend):**

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**3. Reinicie os serviços:**

```bash
docker compose -f infra/docker-compose.yml restart backend frontend
```

**4. Use as credenciais:**
- Email: `admin@nexusclin.com`
- Senha: `admin123`
- Tenant ID: `1`

