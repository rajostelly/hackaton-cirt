from typing import Protocol

from aro.domain.integration.value_objects import ThreatReport, WazuhAgent, WazuhAlert


class VirusTotalGateway(Protocol):
    def get_ip_report(self, ip: str) -> ThreatReport: ...


class WazuhIndexerGateway(Protocol):
    def get_recent_alerts(self, limit: int) -> list[WazuhAlert]: ...
    def get_alert_by_id(self, alert_id: str) -> WazuhAlert | None: ...


class WazuhManagerGateway(Protocol):
    def list_agents(self) -> list[WazuhAgent]: ...
