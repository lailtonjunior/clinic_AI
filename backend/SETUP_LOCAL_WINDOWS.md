# Setup de testes no host Windows (opcional)

## Preparar ambiente
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

## Rodar testes
pytest

## Ambientes e variáveis sensíveis
- Configure `environment` no `.env` com um dos valores `dev`, `staging` ou `prod` (padrão: `dev`).
- Em produção, defina obrigatoriamente `SECRET_KEY` e `ALLOWED_ORIGINS` no `.env`; `ALLOWED_ORIGINS` aceita lista separada por vírgula para múltiplas origens.
