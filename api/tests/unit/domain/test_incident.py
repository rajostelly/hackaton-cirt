from aro.domain.incident.services import (
    detect_lateral_movement,
    detect_traffic_spike,
    ip_segment,
)


def test_ip_segment_internal() -> None:
    assert ip_segment("192.168.10.5") == "192.168.10"
    assert ip_segment("10.4.1.2") == "10.4"
    assert ip_segment("172.16.0.1") == "172.16"


def test_ip_segment_external_is_none() -> None:
    assert ip_segment("8.8.8.8") is None
    assert ip_segment("203.0.113.5") is None
    assert ip_segment("not-an-ip") is None


def test_detect_traffic_spike() -> None:
    assert detect_traffic_spike(600, 500) is True
    assert detect_traffic_spike(100, 500) is False


def test_detect_lateral_movement_cross_segment() -> None:
    flows = [
        {"source_ip": "192.168.10.5", "dst_ips": ["192.168.20.7", "192.168.10.9"]},
        {"source_ip": "192.168.10.6", "dst_ips": ["192.168.10.1"]},  # même segment
        {"source_ip": "8.8.8.8", "dst_ips": ["192.168.20.1"]},  # source externe ignorée
    ]
    findings = detect_lateral_movement(flows)
    assert len(findings) == 1
    assert findings[0]["source_ip"] == "192.168.10.5"
    assert findings[0]["target_segments"] == ["192.168.20"]
