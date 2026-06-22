import pytest

from aro.application.alerting.dto import IngestAlertInput, TriageAlertInput
from aro.application.alerting.use_cases import (
    GetAlertUseCase,
    IngestAlertUseCase,
    ListOpenAlertsUseCase,
    TriageAlertUseCase,
)
from aro.domain.alerting.entities import Alert
from aro.domain.alerting.exceptions import AlertNotFound
from aro.domain.shared.value_objects import AlertStatus, Criticity
from aro.infrastructure.alerting.memory_repo import InMemoryAlertRepository


class _StubExplainer:
    def __init__(self, text: str = "Explication de test") -> None:
        self.text = text

    def explain(self, alert: Alert) -> str:
        return self.text


def _ingest_input(**overrides: object) -> IngestAlertInput:
    defaults: dict[str, object] = dict(
        title="Port Scan",
        source_ip="10.0.0.1",
        criticity=Criticity.HIGH,
        rule_name="network_port_scan",
    )
    defaults.update(overrides)
    return IngestAlertInput(**defaults)  # type: ignore[arg-type]


def test_ingest_attaches_explanation() -> None:
    repo = InMemoryAlertRepository()
    use_case = IngestAlertUseCase(repository=repo, explainer=_StubExplainer("Scan de ports"))
    result = use_case.execute(_ingest_input())
    assert result.explanation == "Scan de ports"


def test_ingest_stores_alert_in_repo() -> None:
    repo = InMemoryAlertRepository()
    use_case = IngestAlertUseCase(repository=repo, explainer=_StubExplainer())
    result = use_case.execute(_ingest_input())
    assert len(repo.list_open(limit=10, criticity=None)) == 1
    assert repo.list_open(limit=10, criticity=None)[0].title == result.title


def test_ingest_alert_has_open_status() -> None:
    repo = InMemoryAlertRepository()
    result = IngestAlertUseCase(repo, _StubExplainer()).execute(_ingest_input())
    assert result.status == AlertStatus.OPEN


def test_list_open_alerts_returns_all() -> None:
    repo = InMemoryAlertRepository()
    ingest = IngestAlertUseCase(repo, _StubExplainer())
    ingest.execute(_ingest_input(title="A1"))
    ingest.execute(_ingest_input(title="A2"))
    results = ListOpenAlertsUseCase(repo).execute(limit=10)
    assert len(results) == 2


def test_list_open_alerts_filtered_by_criticity() -> None:
    repo = InMemoryAlertRepository()
    ingest = IngestAlertUseCase(repo, _StubExplainer())
    ingest.execute(_ingest_input(criticity=Criticity.HIGH))
    ingest.execute(_ingest_input(criticity=Criticity.LOW))
    results = ListOpenAlertsUseCase(repo).execute(limit=10, criticity=Criticity.HIGH)
    assert len(results) == 1
    assert results[0].criticity == Criticity.HIGH


def test_get_alert_found() -> None:
    repo = InMemoryAlertRepository()
    created = IngestAlertUseCase(repo, _StubExplainer()).execute(_ingest_input())
    result = GetAlertUseCase(repo).execute(created.id)
    assert result.id == created.id


def test_get_alert_not_found() -> None:
    repo = InMemoryAlertRepository()
    with pytest.raises(AlertNotFound):
        GetAlertUseCase(repo).execute("00000000-0000-0000-0000-000000000000")


def test_triage_alert_updates_status() -> None:
    repo = InMemoryAlertRepository()
    created = IngestAlertUseCase(repo, _StubExplainer()).execute(_ingest_input())
    result = TriageAlertUseCase(repo).execute(
        TriageAlertInput(alert_id=created.id, is_false_positive=True)
    )
    assert result.is_false_positive is True
    assert result.status == AlertStatus.TRIAGED


def test_triage_alert_not_found() -> None:
    repo = InMemoryAlertRepository()
    with pytest.raises(AlertNotFound):
        TriageAlertUseCase(repo).execute(
            TriageAlertInput(
                alert_id="00000000-0000-0000-0000-000000000000",
                is_false_positive=False,
            )
        )
