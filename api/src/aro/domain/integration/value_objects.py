from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ThreatReport:
    ip: str
    malicious_count: int
    suspicious_count: int
    harmless_count: int
    total_engines: int

    @property
    def is_malicious(self) -> bool:
        return self.malicious_count > 0

    @property
    def threat_score(self) -> float:
        if self.total_engines == 0:
            return 0.0
        return round(self.malicious_count / self.total_engines, 4)


@dataclass(frozen=True, slots=True)
class WazuhAgent:
    id: str
    name: str
    ip: str
    status: str
    os_name: str | None


@dataclass(frozen=True, slots=True)
class WazuhAlert:
    id: str
    rule_id: str
    rule_description: str
    rule_level: int
    agent_name: str
    source_ip: str | None
    timestamp: str
    full_log: str | None
