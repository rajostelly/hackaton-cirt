from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import StrEnum


class Criticity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(StrEnum):
    OPEN = "open"
    TRIAGED = "triaged"
    CLOSED = "closed"


@dataclass(frozen=True, slots=True)
class AlertId:
    value: uuid.UUID

    @classmethod
    def generate(cls) -> AlertId:
        return cls(value=uuid.uuid4())

    @classmethod
    def from_string(cls, raw: str) -> AlertId:
        return cls(value=uuid.UUID(raw))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class IpAddress:
    value: str

    def __post_init__(self) -> None:
        parts = self.value.split(".")
        if len(parts) != 4 or not all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
            raise ValueError(f"adresse IP invalide: {self.value!r}")

    def __str__(self) -> str:
        return self.value
