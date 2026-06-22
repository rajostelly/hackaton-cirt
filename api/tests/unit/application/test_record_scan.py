from aro.application.detection.dto import ScanDetectionInput
from aro.application.detection.use_cases import RecordScanDetectionUseCase
from aro.domain.detection.value_objects import ScanType
from aro.domain.shared.value_objects import AlertStatus, Criticity
from aro.infrastructure.alerting.memory_repo import InMemoryAlertRepository


def test_record_scan_creates_open_alert() -> None:
    repo = InMemoryAlertRepository()
    use_case = RecordScanDetectionUseCase(repository=repo)

    result = use_case.execute(
        ScanDetectionInput(
            source_ip="203.0.113.9",
            scan_type=ScanType.PORT_SCAN,
            ports=list(range(1, 26)),
            target="sfyrisec.duckdns.org",
        )
    )

    assert result.status == AlertStatus.OPEN
    assert result.criticity == Criticity.HIGH  # 25 ports -> >= 20
    assert result.source_ip == "203.0.113.9"
    assert "Nmap" in result.rule_name
    assert len(repo.list_open(limit=10, criticity=None)) == 1


def test_record_scan_low_criticity_for_small_scan() -> None:
    repo = InMemoryAlertRepository()
    result = RecordScanDetectionUseCase(repo).execute(
        ScanDetectionInput(source_ip="198.51.100.1", ports=[22, 80])
    )
    assert result.criticity == Criticity.LOW
