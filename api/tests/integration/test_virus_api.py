import pytest
from fastapi.testclient import TestClient

from aro.application.virus.use_cases import ListVirusUseCase, LookupVirusUseCase
from aro.domain.virus.entities import VirusReport
from aro.infrastructure.virus.store import VirusStore
from aro.interfaces.http.dependencies import (
    get_list_virus_use_case,
    get_lookup_virus_use_case,
)
from aro.main import app


class _FakeScanner:
    def scan(self, indicator: str, kind: str) -> VirusReport:
        return VirusReport(indicator, kind, malicious=7, suspicious=1, harmless=50, total=58)


@pytest.fixture()
def client() -> TestClient:
    store = VirusStore()
    app.dependency_overrides[get_list_virus_use_case] = lambda: ListVirusUseCase(store)
    app.dependency_overrides[get_lookup_virus_use_case] = lambda: LookupVirusUseCase(
        _FakeScanner(), store
    )
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_list_returns_seed(client: TestClient) -> None:
    data = client.get("/virus").json()
    assert len(data) >= 3
    assert all("score" in r for r in data)


def test_lookup_returns_report(client: TestClient) -> None:
    resp = client.post("/virus/lookup", json={"indicator": "203.0.113.9", "kind": "ip"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["indicator"] == "203.0.113.9"
    assert body["is_malicious"] is True
