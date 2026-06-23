from __future__ import annotations

from typing import Any

import vt

from aro.domain.virus.entities import VirusReport


class VtScanner:
    """Scanner VirusTotal v3 — IP (`/ip_addresses`) et fichiers (`/files`)."""

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def scan(self, indicator: str, kind: str) -> VirusReport:
        if not self._api_key:
            raise RuntimeError("VT_API_KEY non configurée")
        path = f"/ip_addresses/{indicator}" if kind == "ip" else f"/files/{indicator}"
        with vt.Client(self._api_key) as client:
            obj = client.get_object(path)
            stats: dict[str, Any] = obj.last_analysis_stats
            return VirusReport(
                indicator=indicator,
                kind=kind,
                malicious=int(stats.get("malicious", 0)),
                suspicious=int(stats.get("suspicious", 0)),
                harmless=int(stats.get("harmless", 0)),
                total=sum(int(v) for v in stats.values()),
                label=_extract_label(obj),
            )


def _extract_label(obj: Any) -> str | None:
    classification = getattr(obj, "popular_threat_classification", None)
    if isinstance(classification, dict):
        suggested = classification.get("suggested_threat_label")
        if suggested:
            return str(suggested)
    return None
