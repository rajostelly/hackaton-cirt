from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from aro.domain.incident.value_objects import IncidentType
from aro.domain.shared.value_objects import Criticity


@dataclass(frozen=True)
class Incident:
    id: str
    type: IncidentType
    title: str
    description: str
    source_ip: str
    severity: Criticity
    timestamp: datetime
    details: dict[str, Any] = field(default_factory=dict)
