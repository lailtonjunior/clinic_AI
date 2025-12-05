# Setup de testes no host Windows (opcional)

## Preparar ambiente
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

## Rodar testes
pytest
