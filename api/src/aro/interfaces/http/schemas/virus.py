from __future__ import annotations

from pydantic import BaseModel


class VirusLookupIn(BaseModel):
    indicator: str
    kind: str = "ip"  # "ip" | "file"


class VirusReportOut(BaseModel):
    indicator: str
    kind: str
    malicious: int
    suspicious: int
    harmless: int
    total: int
    label: str | None = None
    score: float
    is_malicious: bool
