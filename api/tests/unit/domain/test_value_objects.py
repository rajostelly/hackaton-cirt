import uuid

import pytest

from aro.domain.shared.value_objects import AlertId, Criticity, IpAddress


def test_valid_ip_address() -> None:
    ip = IpAddress("192.168.1.1")
    assert str(ip) == "192.168.1.1"


def test_ip_address_octet_out_of_range() -> None:
    with pytest.raises(ValueError):
        IpAddress("999.0.0.1")


def test_ip_address_wrong_format() -> None:
    with pytest.raises(ValueError):
        IpAddress("not-an-ip")


def test_ip_address_too_few_parts() -> None:
    with pytest.raises(ValueError):
        IpAddress("192.168.1")


def test_alert_id_generate_is_uuid() -> None:
    aid = AlertId.generate()
    assert isinstance(aid.value, uuid.UUID)


def test_alert_id_from_string_roundtrip() -> None:
    raw = str(uuid.uuid4())
    aid = AlertId.from_string(raw)
    assert str(aid) == raw


def test_alert_id_from_string_invalid() -> None:
    with pytest.raises(ValueError):
        AlertId.from_string("not-a-uuid")


def test_criticity_string_values() -> None:
    assert Criticity.LOW == "low"
    assert Criticity.MEDIUM == "medium"
    assert Criticity.HIGH == "high"
    assert Criticity.CRITICAL == "critical"
