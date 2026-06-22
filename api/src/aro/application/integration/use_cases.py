from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from aro.domain.alerting.exceptions import AlertNotFound
from aro.domain.alerting.ports import AlertRepository
from aro.domain.integration.ports import (
    CrowdStrikeGateway,
    PaloAltoGateway,
    VirusTotalGateway,
    WazuhIndexerGateway,
    WazuhManagerGateway,
)
from aro.domain.integration.value_objects import (
    CrowdStrikeDetection,
    PaloAltoThreat,
    SocSourceStatus,
    ThreatReport,
    WazuhAgent,
    WazuhAlert,
)
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


@dataclass
class GetPaloAltoThreatsUseCase:
    paloalto: PaloAltoGateway

    def execute(self, limit: int = 50) -> list[PaloAltoThreat]:
        return self.paloalto.get_recent_threats(limit=limit)


@dataclass
class GetCrowdStrikeDetectionsUseCase:
    crowdstrike: CrowdStrikeGateway

    def execute(self, limit: int = 50) -> list[CrowdStrikeDetection]:
        return self.crowdstrike.get_recent_detections(limit=limit)


@dataclass
class GetSocOverviewUseCase:
    """Sonde chaque source du SOC et renvoie son état pour le dashboard unique.

    Chaque source est interrogée indépendamment : si l'une est hors-ligne
    (ex. Wazuh pas encore installé, firewall injoignable), les autres
    restent affichées.
    """

    wazuh_indexer: WazuhIndexerGateway
    paloalto: PaloAltoGateway
    crowdstrike: CrowdStrikeGateway

    def execute(self, limit: int = 25) -> list[SocSourceStatus]:
        return [
            self._probe("wazuh", lambda: self.wazuh_indexer.get_recent_alerts(limit)),
            self._probe("paloalto", lambda: self.paloalto.get_recent_threats(limit)),
            self._probe("crowdstrike", lambda: self.crowdstrike.get_recent_detections(limit)),
        ]

    @staticmethod
    def _probe(name: str, fetch: Callable[[], Sequence[object]]) -> SocSourceStatus:
        try:
            events = fetch()
        except Exception as exc:
            return SocSourceStatus(
                source=name, online=False, event_count=0, detail=str(exc)[:200]
            )
        return SocSourceStatus(source=name, online=True, event_count=len(events))
