from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from aro.domain.shared.value_objects import AlertId, AlertStatus, Criticity, IpAddress


@dataclass
class Alert:
    id: AlertId
    title: str
    source_ip: IpAddress
    criticity: Criticity
    rule_name: str
    timestamp: datetime
    status: AlertStatus = AlertStatus.OPEN
    destination_ip: IpAddress | None = None
    explanation: str | None = None
    is_false_positive: bool | None = None
    raw_data: dict[str, Any] | None = field(default=None)

    @classmethod
    def create(
        cls,
        title: str,
        source_ip: IpAddress,
        criticity: Criticity,
        rule_name: str,
        destination_ip: IpAddress | None = None,
        raw_data: dict[str, Any] | None = None,
    ) -> Alert:
        return cls(
            id=AlertId.generate(),
            title=title,
            source_ip=source_ip,
            criticity=criticity,
            rule_name=rule_name,
            timestamp=datetime.now(timezone.utc),
            destination_ip=destination_ip,
            raw_data=raw_data,
        )

    def attach_explanation(self, explanation: str) -> None:
        self.explanation = explanation

    def triage(self, is_false_positive: bool) -> None:
        self.is_false_positive = is_false_positive
        self.status = AlertStatus.TRIAGED
