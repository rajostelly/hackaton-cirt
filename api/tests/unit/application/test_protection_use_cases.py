import pytest

from aro.application.protection.use_cases import (
    AutoBlockUseCase,
    BlockIpUseCase,
    ListBlockedUseCase,
    UnblockIpUseCase,
)
from aro.domain.protection.exceptions import ProtectedIpError
from aro.domain.protection.value_objects import ProtectionMode
from aro.infrastructure.protection.memory_blocker import InMemoryBlocker


def test_block_ip_adds_to_blocker() -> None:
    b = InMemoryBlocker()
    BlockIpUseCase(b, frozenset()).execute("203.0.113.9")
    assert b.list_blocked() == ["203.0.113.9"]


def test_block_protected_ip_refused() -> None:
    b = InMemoryBlocker()
    with pytest.raises(ProtectedIpError):
        BlockIpUseCase(b, frozenset({"203.0.113.1"})).execute("203.0.113.1")
    assert b.list_blocked() == []


def test_block_loopback_refused() -> None:
    with pytest.raises(ProtectedIpError):
        BlockIpUseCase(InMemoryBlocker(), frozenset()).execute("127.0.0.1")


def test_block_invalid_ip_raises_value_error() -> None:
    with pytest.raises(ValueError):
        BlockIpUseCase(InMemoryBlocker(), frozenset()).execute("999.0.0.1")


def test_unblock_then_list_empty() -> None:
    b = InMemoryBlocker()
    b.block("203.0.113.9")
    UnblockIpUseCase(b).execute("203.0.113.9")
    assert ListBlockedUseCase(b).execute() == []


def test_autoblock_ips_blocks() -> None:
    b = InMemoryBlocker()
    assert AutoBlockUseCase(b, frozenset()).execute("203.0.113.9", ProtectionMode.IPS) is True
    assert b.list_blocked() == ["203.0.113.9"]


def test_autoblock_ids_is_noop() -> None:
    b = InMemoryBlocker()
    assert AutoBlockUseCase(b, frozenset()).execute("203.0.113.9", ProtectionMode.IDS) is False
    assert b.list_blocked() == []


def test_autoblock_skips_protected() -> None:
    b = InMemoryBlocker()
    result = AutoBlockUseCase(b, frozenset({"203.0.113.9"})).execute(
        "203.0.113.9", ProtectionMode.IPS
    )
    assert result is False
    assert b.list_blocked() == []


def test_autoblock_swallows_blocker_error() -> None:
    class _Boom:
        def block(self, ip: str) -> None:
            raise RuntimeError("firewall down")

        def unblock(self, ip: str) -> None: ...

        def list_blocked(self) -> list[str]:
            return []

    result = AutoBlockUseCase(_Boom(), frozenset()).execute("203.0.113.9", ProtectionMode.IPS)
    assert result is False
