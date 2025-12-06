import httpx

from app.core.config import settings


class AiAssistantService:
    def __init__(self):
        if not settings.ai_api_key or not settings.ai_model_name:
            raise RuntimeError("AI API key ou modelo não configurado")
        self.api_key = settings.ai_api_key
        self.model = settings.ai_model_name

    def gerar_resposta(self, contexto: dict, mensagem_usuario: str) -> str:
        system_prompt = (
            "Você é um assistente clínico de apoio. "
            "Suas respostas são sugestões e não substituem o julgamento profissional. "
            "Nunca invente dados que não estejam no contexto fornecido; se faltar informação, peça mais detalhes."
        )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Contexto paciente: {contexto}"},
                {"role": "user", "content": mensagem_usuario},
            ],
            "temperature": 0.2,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        resp = httpx.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
