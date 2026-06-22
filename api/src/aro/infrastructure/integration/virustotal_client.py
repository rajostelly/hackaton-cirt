from __future__ import annotations

from typing import Any

import vt

from aro.domain.integration.value_objects import ThreatReport


class VirusTotalClient:
    """Adaptateur VirusTotal API v3 — https://docs.virustotal.com/reference/ip-info."""

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def get_ip_report(self, ip: str) -> ThreatReport:
        with vt.Client(self._api_key) as client:
            obj = client.get_object(f"/ip_addresses/{ip}")
            stats: dict[str, Any] = obj.last_analysis_stats
            return ThreatReport(
                ip=ip,
                malicious_count=int(stats.get("malicious", 0)),
                suspicious_count=int(stats.get("suspicious", 0)),
                harmless_count=int(stats.get("harmless", 0)),
                total_engines=sum(int(v) for v in stats.values()),
            )
