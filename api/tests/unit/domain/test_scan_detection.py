from aro.domain.detection.services import classify_scan, scan_rule_name, scan_title
from aro.domain.detection.value_objects import ScanType
from aro.domain.shared.value_objects import Criticity


def test_classify_port_scan_thresholds() -> None:
    assert classify_scan(ScanType.PORT_SCAN, 2) == Criticity.LOW
    assert classify_scan(ScanType.PORT_SCAN, 5) == Criticity.MEDIUM
    assert classify_scan(ScanType.PORT_SCAN, 20) == Criticity.HIGH
    assert classify_scan(ScanType.PORT_SCAN, 100) == Criticity.CRITICAL
    assert classify_scan(ScanType.PORT_SCAN, 1000) == Criticity.CRITICAL


def test_classify_http_and_vuln_scan_are_high() -> None:
    assert classify_scan(ScanType.HTTP_PROBE, 0) == Criticity.HIGH
    assert classify_scan(ScanType.VULN_SCAN, 1) == Criticity.HIGH


def test_scan_rule_name_per_type() -> None:
    assert scan_rule_name(ScanType.PORT_SCAN) == "Nmap Port Scan Detected"
    assert scan_rule_name(ScanType.HTTP_PROBE) == "Nmap HTTP Probe Detected"
    assert scan_rule_name(ScanType.VULN_SCAN) == "Nmap Vulnerability Scan Detected"


def test_scan_title_mentions_source_and_count() -> None:
    title = scan_title(ScanType.PORT_SCAN, "203.0.113.5", 42)
    assert "203.0.113.5" in title
    assert "42" in title
    assert "203.0.113.5" in scan_title(ScanType.HTTP_PROBE, "203.0.113.5", 0)
    assert "203.0.113.5" in scan_title(ScanType.VULN_SCAN, "203.0.113.5", 0)
