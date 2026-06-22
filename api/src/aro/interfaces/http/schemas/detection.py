from __future__ import annotations

from pydantic import BaseModel, Field

from aro.domain.detection.value_objects import ScanType


class ScanDetectionIn(BaseModel):
    source_ip: str
    scan_type: ScanType = ScanType.PORT_SCAN
    ports: list[int] = Field(default_factory=list)
    target: str | None = None
    packet_count: int | None = None
    detail: str | None = None
