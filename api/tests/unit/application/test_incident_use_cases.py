from aro.application.incident.use_cases import (
    AnalyzeIncidentsUseCase,
    ListIncidentsUseCase,
    SimulateIncidentUseCase,
)
from aro.domain.incident.value_objects import IncidentType
from aro.infrastructure.incident.store import IncidentStore


class _FakeCollector:
    def __init__(self, flows: list[dict], total: int) -> None:
        self._flows = flows
        self._total = total

    def capture(self) -> tuple[list[dict], int]:
        return self._flows, self._total


def test_analyze_detects_spike_and_lateral() -> None:
    store = IncidentStore()
    flows = [{"source_ip": "192.168.10.5", "dst_ips": ["192.168.20.7"]}]
    use_case = AnalyzeIncidentsUseCase(_FakeCollector(flows, total=900), store, spike_threshold=500)
    incidents = use_case.execute()
    types = {i.type for i in incidents}
    assert IncidentType.TRAFFIC_SPIKE in types
    assert IncidentType.LATERAL_MOVEMENT in types
    assert len(store.list()) == 2


def test_analyze_quiet_network_no_incident() -> None:
    store = IncidentStore()
    use_case = AnalyzeIncidentsUseCase(_FakeCollector([], total=10), store, spike_threshold=500)
    assert use_case.execute() == []


def test_simulate_creates_examples() -> None:
    store = IncidentStore()
    incidents = SimulateIncidentUseCase(store).execute()
    assert len(incidents) == 2
    assert ListIncidentsUseCase(store).execute()[0].type in {
        IncidentType.LATERAL_MOVEMENT,
        IncidentType.TRAFFIC_SPIKE,
    }
