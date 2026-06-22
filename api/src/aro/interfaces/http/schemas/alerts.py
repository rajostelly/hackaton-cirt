from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from aro.domain.shared.value_objects import AlertStatus, Criticity


class AlertIn(BaseModel):
    title: str = Field(min_length=1)
    source_ip: str
    destination_ip: str | None = None
    criticity: Criticity
    rule_name: str = Field(min_length=1)
    raw_data: dict[str, Any] | None = None


class TriageIn(BaseModel):
    is_false_positive: bool
    analyst_note: str | None = None


class AlertOut(BaseModel):
    id: str
    title: str
    source_ip: str
    destination_ip: str | None = None
    criticity: Criticity
    rule_name: str
    status: AlertStatus
    timestamp: datetime
    explanation: str | None = None
    is_false_positive: bool | None = None


class HealthResponse(BaseModel):
    status: str = "ok"
