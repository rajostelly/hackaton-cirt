from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from aro.domain.incident.value_objects import IncidentType
from aro.domain.shared.value_objects import Criticity


class IncidentOut(BaseModel):
    id: str
    type: IncidentType
    title: str
    description: str
    source_ip: str
    severity: Criticity
    timestamp: datetime
    details: dict[str, Any]
