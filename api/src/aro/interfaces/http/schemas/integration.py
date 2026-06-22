from __future__ import annotations

from pydantic import BaseModel


class ThreatReportOut(BaseModel):
    ip: str
    malicious_count: int
    suspicious_count: int
    harmless_count: int
    total_engines: int
    is_malicious: bool
    threat_score: float


class WazuhAgentOut(BaseModel):
    id: str
    name: str
    ip: str
    status: str
    os_name: str | None = None


class WazuhAlertOut(BaseModel):
    id: str
    rule_id: str
    rule_description: str
    rule_level: int
    agent_name: str
    source_ip: str | None = None
    timestamp: str
    full_log: str | None = None


class PaloAltoThreatOut(BaseModel):
    id: str
    threat_name: str
    severity: str
    action: str
    source_ip: str
    destination_ip: str
    application: str | None = None
    timestamp: str


class CrowdStrikeDetectionOut(BaseModel):
    id: str
    detection_name: str
    severity: str
    tactic: str | None = None
    technique: str | None = None
    hostname: str
    status: str
    timestamp: str


class SocSourceStatusOut(BaseModel):
    source: str
    online: bool
    event_count: int
    detail: str | None = None


class SocOverviewOut(BaseModel):
    sources: list[SocSourceStatusOut]
