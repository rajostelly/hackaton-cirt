from __future__ import annotations

from typing import Any

import httpx

from aro.domain.integration.value_objects import WazuhAgent


class WazuhManagerClient:
    """Adaptateur Wazuh Manager REST API — port 55000.

    Doc: https://documentation.wazuh.com/current/user-manual/api/reference.html
    Auth: JWT via POST /security/user/authenticate
    """

    def __init__(
        self,
        base_url: str,
        user: str,
        password: str,
        verify_ssl: bool = False,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._user = user
        self._password = password
        self._verify_ssl = verify_ssl
        self._token: str | None = None

    def _auth_headers(self) -> dict[str, str]:
        if self._token is None:
            self._token = self._authenticate()
        return {"Authorization": f"Bearer {self._token}"}

    def _authenticate(self) -> str:
        resp = httpx.post(
            f"{self._base_url}/security/user/authenticate",
            auth=(self._user, self._password),
            verify=self._verify_ssl,
        )
        resp.raise_for_status()
        return str(resp.json()["data"]["token"])

    def list_agents(self) -> list[WazuhAgent]:
        resp = httpx.get(
            f"{self._base_url}/agents",
            headers=self._auth_headers(),
            params={"limit": 500, "status": "active,disconnected,never_connected"},
            verify=self._verify_ssl,
        )
        if resp.status_code == 401:
            # Token expired — renew once
            self._token = self._authenticate()
            resp = httpx.get(
                f"{self._base_url}/agents",
                headers=self._auth_headers(),
                params={"limit": 500},
                verify=self._verify_ssl,
            )
        resp.raise_for_status()
        items: list[dict[str, Any]] = resp.json()["data"]["affected_items"]
        return [self._to_agent(a) for a in items]

    @staticmethod
    def _to_agent(data: dict[str, Any]) -> WazuhAgent:
        os_info: dict[str, Any] | None = data.get("os")
        return WazuhAgent(
            id=str(data["id"]),
            name=str(data["name"]),
            ip=str(data.get("ip", "unknown")),
            status=str(data.get("status", "unknown")),
            os_name=str(os_info["name"]) if os_info else None,
        )
