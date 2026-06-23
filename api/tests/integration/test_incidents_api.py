import pytest
from fastapi.testclient import TestClient

from aro.application.incident.use_cases import (
    AnalyzeIncidentsUseCase,
    ListIncidentsUseCase,
    SimulateIncidentUseCase,
)
from aro.infrastructure.incident.store import IncidentStore
from aro.interfaces.http.dependencies import (
    get_analyze_incidents_use_case,
    get_incident_repository,
    get_list_incidents_use_case,
    get_simulate_incident_use_case,
)
from aro.main import app


class _FakeCollector:
    def capture(self) -> tuple[list[dict], int]:
        return [{"source_ip": "192.168.10.5", "dst_ips": ["192.168.20.7"]}], 900


@pytest.fixture()
def client() -> TestClient:
    store = IncidentStore()
    app.dependency_overrides[get_incident_repository] = lambda: store
    app.dependency_overrides[get_list_incidents_use_case] = lambda: ListIncidentsUseCase(store)
    app.dependency_overrides[get_simulate_incident_use_case] = (
        lambda: SimulateIncidentUseCase(store)
    )
    app.dependency_overrides[get_analyze_incidents_use_case] = lambda: AnalyzeIncidentsUseCase(
        _FakeCollector(), store, spike_threshold=500
    )
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_list_empty(client: TestClient) -> None:
    assert client.get("/incidents").json() == []


def test_simulate_then_list(client: TestClient) -> None:
    resp = client.post("/incidents/simulate")
    assert resp.status_code == 200
    assert len(resp.json()) == 2
    assert len(client.get("/incidents").json()) == 2


def test_analyze_detects(client: TestClient) -> None:
    data = client.post("/incidents/analyze").json()
    types = {i["type"] for i in data}
    assert "traffic_spike" in types
    assert "lateral_movement" in types
