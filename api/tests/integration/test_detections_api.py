import pytest
from fastapi.testclient import TestClient

from aro.domain.alerting.entities import Alert
from aro.domain.shared.value_objects import AlertId, Criticity, IpAddress
from aro.infrastructure.alerting.memory_repo import InMemoryAlertRepository
from aro.infrastructure.realtime.broker import AlertBroker
from aro.interfaces.http.dependencies import get_explainer, get_repository
from aro.interfaces.http.routers import detections
from aro.main import app


class _StubExplainer:
    def explain(self, alert: Alert) -> str:
        return "Explication IA de test"


@pytest.fixture()
def repo() -> InMemoryAlertRepository:
    return InMemoryAlertRepository()


@pytest.fixture()
def client(repo: InMemoryAlertRepository) -> TestClient:
    app.dependency_overrides[get_repository] = lambda: repo
    app.dependency_overrides[get_explainer] = lambda: _StubExplainer()
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_report_port_scan_creates_high_alert(client: TestClient) -> None:
    resp = client.post(
        "/detections/scan",
        json={
            "source_ip": "203.0.113.7",
            "scan_type": "port_scan",
            "ports": list(range(1, 30)),
            "target": "sfyrisec.duckdns.org",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["criticity"] == "high"
    assert "nmap" in data["rule_name"].lower()
    assert data["status"] == "open"


def test_reported_scan_appears_in_open_alerts(client: TestClient) -> None:
    created = client.post(
        "/detections/scan",
        json={"source_ip": "198.51.100.23", "ports": [22, 80, 443]},
    ).json()
    listed = client.get("/alerts").json()
    assert any(a["id"] == created["id"] for a in listed)


def test_report_scan_invalid_ip_is_rejected(client: TestClient) -> None:
    resp = client.post(
        "/detections/scan",
        json={"source_ip": "999.999.0.1", "ports": [1]},
    )
    assert resp.status_code == 422


def test_enrich_with_ai_attaches_explanation(repo: InMemoryAlertRepository, monkeypatch) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "fake-key")
    alert = Alert.create(
        title="t", source_ip=IpAddress("1.2.3.4"), criticity=Criticity.HIGH, rule_name="r"
    )
    repo.add(alert)
    detections.enrich_with_ai(str(alert.id), repo, _StubExplainer(), AlertBroker())
    assert repo.get_by_id(alert.id).explanation == "Explication IA de test"


def test_enrich_with_ai_falls_back_on_error(repo: InMemoryAlertRepository, monkeypatch) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "fake-key")

    class _Boom:
        def explain(self, alert: Alert) -> str:
            raise RuntimeError("API down")

    alert = Alert.create(
        title="t", source_ip=IpAddress("1.2.3.4"), criticity=Criticity.HIGH, rule_name="r"
    )
    repo.add(alert)
    detections.enrich_with_ai(str(alert.id), repo, _Boom(), AlertBroker())
    assert repo.get_by_id(alert.id).explanation  # explication de repli non vide


def test_enrich_with_ai_missing_alert_is_noop(repo: InMemoryAlertRepository) -> None:
    # Ne doit pas lever même si l'alerte n'existe pas.
    detections.enrich_with_ai(str(AlertId.generate()), repo, _StubExplainer(), AlertBroker())
