from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from aro.domain.shared.value_objects import AlertStatus, Criticity


@dataclass
class IngestAlertInput:
    title: str
    source_ip: str
    criticity: Criticity
    rule_name: str
    destination_ip: str | None = None
    raw_data: dict[str, Any] | None = None


@dataclass
class TriageAlertInput:
    alert_id: str
    is_false_positive: bool
    analyst_note: str | None = None


@dataclass
class AlertOutput:
    id: str
    title: str
    source_ip: str
    criticity: Criticity
    rule_name: str
    status: AlertStatus
    timestamp: datetime
    destination_ip: str | None = None
    explanation: str | None = None
    is_false_positive: bool | None = None
