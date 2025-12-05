# NexusClin

PEP multiprofissional + gestao clinica + faturamento SUS (BPA-I/APAC) para CER/APAEs, alinhado ao layout DATASUS Nov/2025.

## Estrutura
- `backend/`: FastAPI + SQLAlchemy + Alembic + Celery stub
- `frontend/`: Next.js 14 App Router + Tailwind + Tiptap
- `infra/`: docker-compose para db/redis/minio/backend/frontend
- `shared/`: espaco para tipos/fixtures/regra de dominio comuns

## Como rodar (dev)
1. Crie `.env` em `backend/` (use `.env.example`).
2. Suba dependencias:
   ```sh
   cd infra
   docker compose up -d db redis minio
   ```
3. Build/rodar backend+frontend:
   ```sh
   docker compose up -d backend frontend
   ```
4. Rodar migracao:
   ```sh
   docker compose exec backend alembic upgrade head
   ```
5. (Opcional) Seed minimo via psql ou shells do backend.

Backend em `http://localhost:8000`, Frontend em `http://localhost:3000`.

## Testes
```sh
cd backend
pytest
```

### Rodando testes no Windows 11 (Docker)
```powershell
cd infra
docker compose exec backend pytest
```

### Rodando testes no host Windows (opcional)
Consulte backend/SETUP_LOCAL_WINDOWS.md

## Validacao Real Pre-Piloto
- Preparar fixture anonima em `backend/app/tests/fixtures/real_competencia/`.
- Rodar validacao de ponta a ponta com comparacao opcional a arquivos aceitos no MAG:
```powershell
cd infra
docker compose exec backend python -m app.scripts.validate_real_competencia 202501 --fixture app/tests/fixtures/real_competencia/sample_202501.json
```
- Se tiver arquivos de referencia:
```powershell
docker compose exec backend python -m app.scripts.validate_real_competencia 202501 --fixture app/tests/fixtures/real_competencia/sample_202501.json --ref-bpa /caminho/bpa_ref.rem --ref-apac /caminho/apac_ref.rem
```
- Saidas geradas em `backend/app/tests/output/` (BPA/APAC + relatorio diff se houver divergencias).

## SIGTAP real (sync mensal)
- Variaveis de ambiente: `SIGTAP_BASE_URL` (pode conter `{competencia}`), `SIGTAP_ADMIN_TOKEN` (header `X-Admin-Token`), `SIGTAP_JOB_ENABLED`, `SIGTAP_JOB_INTERVAL_HOURS`.
- Sync manual: `POST /api/sigtap/sync?competencia=AAAAMM` com header `X-Admin-Token`.
- Status: `GET /api/sigtap/status` com o mesmo header.
- Job automatico: iniciado no startup, verifica diariamente se a competencia atual ja foi importada e baixa do DATASUS se faltar (nao sobrescreve historicos).
- Erros de download retornam 400 e nao gravam nada no banco.
- Teste de regressao: `backend/app/tests/test_sigtap_sync_realistic.py` (mock zip com duas competencias e validacao de vigencia/regras).

## Proximos passos
- Completar validacoes SIGTAP/CID/CNS/CPF e trilha de auditoria
- Integrar fluxo real de exportacao BPA-I/APAC com dados do banco
- Implementar RBAC/MFA e assinatura ICP-Brasil (feature flag)

## Rodando no Windows 11 (Docker Desktop)
```powershell
cd infra
docker compose down
docker compose up -d db redis minio
docker compose up -d --build backend frontend
docker compose exec backend alembic upgrade head
docker compose exec backend pytest
```

URLs:

Frontend: http://localhost:3000

Backend: http://localhost:8000/docs

MinIO Console: http://localhost:9003

MinIO API (host): http://localhost:9002

Observacao:

O compose ja mapeia o Postgres para 5433:5432 no host para evitar conflito com instalacoes locais. Se 5433 tambem estiver ocupada, ajuste apenas o lado esquerdo do mapeamento conforme necessario.

## RBAC, isolamento e auditoria
- Login (POST /api/auth/login) retorna JWT com tenant_id e roles do usuario no tenant; frontend armazena em localStorage.
- Roles: SUPER_ADMIN, ADMIN_TENANT, FATURAMENTO, CLINICO, RECEPCAO, AUDITOR_INTERNO. Export BPA/APAC e sync SIGTAP exigem FATURAMENTO/ADMIN_TENANT; cadastro paciente/agenda/atendimento exige RECEPCAO/CLINICO/ADMIN_TENANT; leituras filtram por tenant_id.
- Trilha de auditoria em audit_logs via audit_log_service.log_action em operacoes criticas (paciente, atendimento, procedimento, exports, sync SIGTAP).
- Frontend esconde menus conforme role e envia Authorization Bearer em chamadas.
- Teste automatizado: backend/app/tests/test_rbac_isolamento.py cobre isolamento e auditoria.

