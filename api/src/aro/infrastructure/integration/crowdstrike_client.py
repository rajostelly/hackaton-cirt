from __future__ import annotations

from typing import Any

import httpx

from aro.domain.integration.value_objects import CrowdStrikeDetection


class CrowdStrikeClient:
    """Adaptateur CrowdStrike Falcon — OAuth2 + Alerts API.

    Flux :
      1. POST /oauth2/token (client_id + client_secret) -> bearer token ;
      2. GET  /alerts/queries/alerts/v2 -> liste d'ids ;
      3. POST /alerts/entities/alerts/v2 -> détails des alertes.

    Doc: https://falcon.crowdstrike.com/documentation/page/a2a7fc0e/crowdstrike-oauth2-based-apis
    base_url dépend de la région du tenant :
      us-1: https://api.crowdstrike.com | us-2: https://api.us-2.crowdstrike.com
      eu-1: https://api.eu-1.crowdstrike.com
    """

    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
        verify_ssl: bool = True,
        timeout: float = 30.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._client_id = client_id
        self._client_secret = client_secret
        self._verify_ssl = verify_ssl
        self._timeout = timeout

    def get_recent_detections(self, limit: int = 50) -> list[CrowdStrikeDetection]:
        if not self._client_id or not self._client_secret:
            raise RuntimeError(
                "CrowdStrike non configuré (CROWDSTRIKE_CLIENT_ID / CROWDSTRIKE_CLIENT_SECRET)"
            )
        with httpx.Client(verify=self._verify_ssl, timeout=self._timeout) as client:
            token = self._get_token(client)
            headers = {"Authorization": f"Bearer {token}"}
            ids = self._query_alert_ids(client, headers, limit)
            if not ids:
                return []
            return self._fetch_alerts(client, headers, ids)

    def _get_token(self, client: httpx.Client) -> str:
        resp = client.post(
            f"{self._base_url}/oauth2/token",
            data={"client_id": self._client_id, "client_secret": self._client_secret},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        resp.raise_for_status()
        return str(resp.json()["access_token"])

    def _query_alert_ids(
        self, client: httpx.Client, headers: dict[str, str], limit: int
    ) -> list[str]:
        resp = client.get(
            f"{self._base_url}/alerts/queries/alerts/v2",
            headers=headers,
            params={"limit": limit, "sort": "created_timestamp.desc"},
        )
        resp.raise_for_status()
        resources: list[str] = resp.json().get("resources", [])
        return resources

    def _fetch_alerts(
        self, client: httpx.Client, headers: dict[str, str], ids: list[str]
    ) -> list[CrowdStrikeDetection]:
        resp = client.post(
            f"{self._base_url}/alerts/entities/alerts/v2",
            headers={**headers, "Content-Type": "application/json"},
            json={"composite_ids": ids},
        )
        resp.raise_for_status()
        resources: list[dict[str, Any]] = resp.json().get("resources", [])
        return [self._to_detection(r) for r in resources]

    @staticmethod
    def _to_detection(raw: dict[str, Any]) -> CrowdStrikeDetection:
        device: dict[str, Any] = raw.get("device") or {}
        behaviors: list[dict[str, Any]] = raw.get("behaviors") or []
        first: dict[str, Any] = behaviors[0] if behaviors else {}
        return CrowdStrikeDetection(
            id=str(raw.get("composite_id") or raw.get("id") or raw.get("detection_id") or ""),
            detection_name=str(
                raw.get("display_name") or raw.get("name") or first.get("display_name") or "Detection"
            ),
            severity=str(
                raw.get("severity_name")
                or raw.get("max_severity_displayname")
                or raw.get("severity")
                or "unknown"
            ),
            tactic=raw.get("tactic") or first.get("tactic"),
            technique=raw.get("technique") or first.get("technique"),
            hostname=str(device.get("hostname") or raw.get("hostname") or "unknown"),
            status=str(raw.get("status") or "new"),
            timestamp=str(raw.get("created_timestamp") or raw.get("timestamp") or ""),
        )
