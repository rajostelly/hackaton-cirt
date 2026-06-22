from __future__ import annotations

from dataclasses import dataclass, field

from aro.domain.detection.value_objects import ScanType


@dataclass
class ScanDetectionInput:
    source_ip: str
    scan_type: ScanType = ScanType.PORT_SCAN
    ports: list[int] = field(default_factory=list)
    target: str | None = None
    packet_count: int | None = None
    detail: str | None = None
