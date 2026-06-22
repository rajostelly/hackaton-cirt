from __future__ import annotations

from typing import Any

from opensearchpy import OpenSearch

from aro.domain.integration.value_objects import WazuhAlert

_WAZUH_INDEX = "wazuh-alerts-*"


class WazuhIndexerClient:
    """Adaptateur Wazuh Indexer (OpenSearch) — port 9200.

    Wazuh Indexer est compatible OpenSearch/Elasticsearch.
    Doc: https://documentation.wazuh.com/current/user-manual/wazuh-indexer/index.html
    """

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        verify_certs: bool = False,
    ) -> None:
        self._client = OpenSearch(
            hosts=[{"host": host, "port": port}],
            http_auth=(user, password),
            use_ssl=True,
            verify_certs=verify_certs,
            ssl_show_warn=False,
        )

    def get_recent_alerts(self, limit: int = 50) -> list[WazuhAlert]:
        body: dict[str, Any] = {
            "query": {"match_all": {}},
            "sort": [{"@timestamp": {"order": "desc"}}],
            "size": limit,
        }
        resp = self._client.search(index=_WAZUH_INDEX, body=body)
        return [self._hit_to_alert(h) for h in resp["hits"]["hits"]]

    def get_alert_by_id(self, alert_id: str) -> WazuhAlert | None:
        resp = self._client.search(
            index=_WAZUH_INDEX,
            body={"query": {"term": {"_id": alert_id}}, "size": 1},
        )
        hits: list[dict[str, Any]] = resp["hits"]["hits"]
        return self._hit_to_alert(hits[0]) if hits else None

    @staticmethod
    def _hit_to_alert(hit: dict[str, Any]) -> WazuhAlert:
        src: dict[str, Any] = hit["_source"]
        rule: dict[str, Any] = src.get("rule", {})
        agent: dict[str, Any] = src.get("agent", {})
        data: dict[str, Any] = src.get("data", {})
        return WazuhAlert(
            id=hit["_id"],
            rule_id=str(rule.get("id", "")),
            rule_description=str(rule.get("description", "")),
            rule_level=int(rule.get("level", 0)),
            agent_name=str(agent.get("name", "unknown")),
            source_ip=data.get("srcip") or agent.get("ip"),
            timestamp=str(src.get("@timestamp", "")),
            full_log=src.get("full_log"),
        )
