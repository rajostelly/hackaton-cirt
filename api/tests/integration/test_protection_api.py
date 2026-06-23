import pytest
from fastapi.testclient import TestClient

from aro.application.protection.use_cases import (
    BlockIpUseCase,
    ListBlockedUseCase,
    UnblockIpUseCase,
)
from aro.domain.protection.value_objects import ProtectionMode
from aro.infrastructure.protection.memory_blocker import InMemoryBlocker
from aro.infrastructure.protection.settings import ProtectionSettings
from aro.interfaces.http.dependencies import (
    get_block_use_case,
    get_list_blocked_use_case,
    get_protection_settings,
    get_unblock_use_case,
)
from aro.main import app


@pytest.fixture()
def client() -> TestClient:
    blocker = InMemoryBlocker()
    settings = ProtectionSettings()
    app.dependency_overrides[get_block_use_case] = lambda: BlockIpUseCase(
        blocker, frozenset({"10.0.0.1"})
    )
    app.dependency_overrides[get_unblock_use_case] = lambda: UnblockIpUseCase(blocker)
    app.dependency_overrides[get_list_blocked_use_case] = lambda: ListBlockedUseCase(blocker)
    app.dependency_overrides[get_protection_settings] = lambda: settings
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_default_mode_is_ids(client: TestClient) -> None:
    assert client.get("/protection/mode").json()["mode"] == "ids"


def test_switch_to_ips(client: TestClient) -> None:
    resp = client.put("/protection/mode", json={"mode": "ips"})
    assert resp.status_code == 200
    assert resp.json()["mode"] == "ips"


def test_block_then_listed(client: TestClient) -> None:
    resp = client.post("/protection/block", json={"source_ip": "203.0.113.50"})
    assert resp.status_code == 201
    assert "203.0.113.50" in resp.json()["blocked"]
    assert "203.0.113.50" in client.get("/protection/blocked").json()["blocked"]


def test_block_protected_ip_returns_409(client: TestClient) -> None:
    assert client.post("/protection/block", json={"source_ip": "10.0.0.1"}).status_code == 409


def test_block_invalid_ip_returns_422(client: TestClient) -> None:
    assert client.post("/protection/block", json={"source_ip": "999.0.0.1"}).status_code == 422


def test_unblock_removes_ip(client: TestClient) -> None:
    client.post("/protection/block", json={"source_ip": "203.0.113.50"})
    resp = client.post("/protection/unblock", json={"source_ip": "203.0.113.50"})
    assert "203.0.113.50" not in resp.json()["blocked"]


def test_auto_block_helper_blocks_in_ips_mode() -> None:
    from aro.interfaces.http import dependencies as deps

    deps.reset_protection()
    deps.get_protection_settings().mode = ProtectionMode.IPS
    try:
        assert deps.auto_block("203.0.113.99") is True
        assert "203.0.113.99" in deps.get_blocker().list_blocked()
    finally:
        deps.reset_protection()
