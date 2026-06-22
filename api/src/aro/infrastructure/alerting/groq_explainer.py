from __future__ import annotations

import os

from groq import Groq

from aro.domain.alerting.entities import Alert

# Modèle gratuit Groq — 1 000 req/jour sur le free tier
# Alternatives : llama-3.1-8b-instant (14 400 req/jour, moins puissant)
# Doc: https://console.groq.com/docs/models
DEFAULT_MODEL = "llama-3.3-70b-versatile"


class GroqExplainer:
    """Explainer IA via Groq API (OpenAI-compatible)."""

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
    ) -> None:
        self._client = Groq(api_key=api_key)
        self._model = model

    def explain(self, alert: Alert) -> str:
        completion = self._client.chat.completions.create(
            model=self._model,
            max_tokens=400,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es un analyste SOC expert en cybersécurité. "
                        "Réponds toujours en français, de façon concise et actionnable."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Explique cette alerte de sécurité en 2-3 phrases.\n\n"
                        f"Alerte : {alert.title}\n"
                        f"IP source : {alert.source_ip}\n"
                        f"Règle déclenchée : {alert.rule_name}\n"
                        f"Criticité : {alert.criticity}"
                    ),
                },
            ],
        )
        return completion.choices[0].message.content or ""
