from __future__ import annotations

from typing import Protocol

from aro.domain.incident.entities import Incident


class IncidentRepository(Protocol):
    def add(self, incident: Incident) -> None: ...
    def list(self, limit: int = 100) -> list[Incident]: ...
