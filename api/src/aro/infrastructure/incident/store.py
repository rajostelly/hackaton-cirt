from __future__ import annotations

from collections import deque

from aro.domain.incident.entities import Incident


class IncidentStore:
    """Tampon circulaire en mémoire des incidents récents (plus récent d'abord)."""

    def __init__(self, maxlen: int = 200) -> None:
        self._items: deque[Incident] = deque(maxlen=maxlen)

    def add(self, incident: Incident) -> None:
        self._items.appendleft(incident)

    def list(self, limit: int = 100) -> list[Incident]:
        return list(self._items)[:limit]
