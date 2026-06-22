from __future__ import annotations

from dataclasses import dataclass

from aro.domain.alerting.exceptions import AlertNotFound
from aro.domain.alerting.ports import AlertRepository
from aro.domain.integration.ports import (
    VirusTotalGateway,
    WazuhIndexerGateway,
    WazuhManagerGateway,
)
from aro.domain.integration.value_objects import ThreatReport, WazuhAgent, WazuhAlert
from aro.domain.shared.value_objects import AlertId


@dataclass
class EnrichAlertWithVirusTotalUseCase:
    repository: AlertRepository
    vt_gateway: VirusTotalGateway

    def execute(self, alert_id: str) -> ThreatReport:
        alert = self.repository.get_by_id(AlertId.from_string(alert_id))
        if alert is None:
            raise AlertNotFound(alert_id)
        return self.vt_gateway.get_ip_report(str(alert.source_ip))


@dataclass
class ListWazuhAgentsUseCase:
    wazuh_manager: WazuhManagerGateway

    def execute(self) -> list[WazuhAgent]:
        return self.wazuh_manager.list_agents()


@dataclass
class GetWazuhAlertsUseCase:
    wazuh_indexer: WazuhIndexerGateway

    def execute(self, limit: int = 50) -> list[WazuhAlert]:
        return self.wazuh_indexer.get_recent_alerts(limit=limit)
