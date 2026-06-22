import pytest

from aro.application.integration.use_cases import (
    EnrichAlertWithVirusTotalUseCase,
    GetWazuhAlertsUseCase,
    ListWazuhAgentsUseCase,
)
from aro.domain.alerting.entities import Alert
from aro.domain.alerting.exceptions import AlertNotFound
from aro.domain.integration.value_objects import ThreatReport, WazuhAgent, WazuhAlert
from aro.domain.shared.value_objects import Criticity, IpAddress
from aro.infrastructure.alerting.memory_repo import InMemoryAlertRepository


# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------

class _StubVirusTotal:
    def __init__(self, report: ThreatReport) -> None:
        self._report = report

    def get_ip_report(self, ip: str) -> ThreatReport:
        return self._report


class _StubWazuhManager:
    def __init__(self, agents: list[WazuhAgent]) -> None:
        self._agents = agents

    def list_agents(self) -> list[WazuhAgent]:
        return self._agents


class _StubWazuhIndexer:
    def __init__(self, alerts: list[WazuhAlert]) -> None:
        self._alerts = alerts

    def get_recent_alerts(self, limit: int) -> list[WazuhAlert]:
        return self._alerts[:limit]

    def get_alert_by_id(self, alert_id: str) -> WazuhAlert | None:
        return next((a for a in self._alerts if a.id == alert_id), None)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _add_alert(repo: InMemoryAlertRepository) -> Alert:
    alert = Alert.create(
        title="Port Scan",
        source_ip=IpAddress("10.0.0.1"),
        criticity=Criticity.HIGH,
        rule_name="port_scan",
    )
    repo.add(alert)
    return alert


def _make_threat_report(ip: str = "10.0.0.1", malicious: int = 3) -> ThreatReport:
    return ThreatReport(
        ip=ip,
        malicious_count=malicious,
        suspicious_count=1,
        harmless_count=60,
        total_engines=70,
    )


# ---------------------------------------------------------------------------
# ThreatReport value object
# ---------------------------------------------------------------------------

def test_threat_report_is_malicious_when_count_gt_zero() -> None:
    report = _make_threat_report(malicious=5)
    assert report.is_malicious is True


def test_threat_report_not_malicious_when_zero() -> None:
    report = _make_threat_report(malicious=0)
    assert report.is_malicious is False


def test_threat_score_ratio() -> None:
    report = ThreatReport(ip="1.1.1.1", malicious_count=10, suspicious_count=0, harmless_count=90, total_engines=100)
    assert report.threat_score == 0.1


def test_threat_score_zero_engines() -> None:
    report = ThreatReport(ip="1.1.1.1", malicious_count=0, suspicious_count=0, harmless_count=0, total_engines=0)
    assert report.threat_score == 0.0


# ---------------------------------------------------------------------------
# EnrichAlertWithVirusTotalUseCase
# ---------------------------------------------------------------------------

def test_enrich_returns_report_for_source_ip() -> None:
    repo = InMemoryAlertRepository()
    alert = _add_alert(repo)
    report = _make_threat_report(ip="10.0.0.1")
    use_case = EnrichAlertWithVirusTotalUseCase(repository=repo, vt_gateway=_StubVirusTotal(report))

    result = use_case.execute(str(alert.id))

    assert result.ip == "10.0.0.1"
    assert result.malicious_count == 3


def test_enrich_raises_when_alert_not_found() -> None:
    repo = InMemoryAlertRepository()
    use_case = EnrichAlertWithVirusTotalUseCase(
        repository=repo, vt_gateway=_StubVirusTotal(_make_threat_report())
    )
    with pytest.raises(AlertNotFound):
        use_case.execute("00000000-0000-0000-0000-000000000000")


# ---------------------------------------------------------------------------
# ListWazuhAgentsUseCase
# ---------------------------------------------------------------------------

def test_list_agents_returns_all() -> None:
    agents = [
        WazuhAgent(id="001", name="web-server", ip="192.168.1.10", status="active", os_name="Ubuntu"),
        WazuhAgent(id="002", name="db-server", ip="192.168.1.11", status="active", os_name="CentOS"),
    ]
    use_case = ListWazuhAgentsUseCase(wazuh_manager=_StubWazuhManager(agents))
    result = use_case.execute()
    assert len(result) == 2
    assert result[0].name == "web-server"


# ---------------------------------------------------------------------------
# GetWazuhAlertsUseCase
# ---------------------------------------------------------------------------

def _make_wazuh_alert(alert_id: str = "abc123") -> WazuhAlert:
    return WazuhAlert(
        id=alert_id,
        rule_id="5710",
        rule_description="SSH brute force",
        rule_level=10,
        agent_name="web-server",
        source_ip="203.0.113.5",
        timestamp="2026-06-21T10:00:00.000Z",
        full_log=None,
    )


def test_get_wazuh_alerts_respects_limit() -> None:
    alerts = [_make_wazuh_alert(f"id{i}") for i in range(10)]
    use_case = GetWazuhAlertsUseCase(wazuh_indexer=_StubWazuhIndexer(alerts))
    result = use_case.execute(limit=3)
    assert len(result) == 3
