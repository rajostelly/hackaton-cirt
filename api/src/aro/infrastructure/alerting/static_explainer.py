from __future__ import annotations

from aro.domain.alerting.entities import Alert

DEFAULT_EXPLANATION = (
    "Activité de balayage réseau (type nmap) détectée. "
    "Identifiez la source, bloquez l'adresse si elle n'est pas autorisée et "
    "surveillez toute tentative d'exploitation consécutive."
)


class StaticExplainer:
    """Explainer de repli, sans appel réseau (utilisé sans clé Groq)."""

    def __init__(self, text: str = DEFAULT_EXPLANATION) -> None:
        self._text = text

    def explain(self, alert: Alert) -> str:
        return self._text
