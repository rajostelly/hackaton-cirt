from aro.domain.protection.services import is_protected_ip
from aro.domain.protection.value_objects import ProtectionMode


def test_protection_mode_values() -> None:
    assert ProtectionMode.IDS == "ids"
    assert ProtectionMode.IPS == "ips"


def test_is_protected_ip() -> None:
    assert is_protected_ip("127.0.0.1", [])
    assert is_protected_ip("0.0.0.0", [])
    assert is_protected_ip("10.0.0.5", ["10.0.0.5"])
    assert not is_protected_ip("203.0.113.9", ["10.0.0.5"])
