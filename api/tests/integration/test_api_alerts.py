import pytest
from fastapi.testclient import TestClient

from aro.domain.alerting.entities import Alert
from aro.infrastructure.alerting.memory_repo import InMemoryAlertRepository
from aro.interfaces.http.dependencies import get_explainer, get_repository
from aro.main import app


class _StubExplainer:
    def explain(self, alert: Alert) -> str:
        return "Explication de test intégration"


@pytest.fixture()
def client() -> TestClient:
    repo = InMemoryAlertRepository()
    app.dependency_overrides[get_repository] = lambda: repo
    app.dependency_overrides[get_explainer] = lambda: _StubExplainer()
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health_check(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_list_alerts_initially_empty(client: TestClient) -> None:
    resp = client.get("/alerts")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_alert(client: TestClient) -> None:
    resp = client.post(
        "/alerts",
        json={
            "title": "Port Scan Detected",
            "source_ip": "192.168.1.100",
            "criticity": "high",
            "rule_name": "network_port_scan",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Port Scan Detected"
    assert data["criticity"] == "high"
    assert data["status"] == "open"
    assert data["explanation"] == "Explication de test intégration"


def test_create_then_list(client: TestClient) -> None:
    client.post(
        "/alerts",
        json={
            "title": "Phishing Link",
            "source_ip": "10.0.0.5",
            "criticity": "critical",
            "rule_name": "phishing_detection",
        },
    )
    resp = client.get("/alerts")
    assert len(resp.json()) == 1


def test_get_alert_by_id(client: TestClient) -> None:
    create_resp = client.post(
        "/alerts",
        json={
            "title": "Bruteforce SSH",
            "source_ip": "172.16.0.1",
            "criticity": "medium",
            "rule_name": "ssh_bruteforce",
        },
    )
    alert_id = create_resp.json()["id"]
    resp = client.get(f"/alerts/{alert_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == alert_id


def test_get_alert_not_found(client: TestClient) -> None:
    resp = client.get("/alerts/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_triage_alert(client: TestClient) -> None:
    create_resp = client.post(
        "/alerts",
        json={
            "title": "Suspicious DNS",
            "source_ip": "10.10.10.10",
            "criticity": "low",
            "rule_name": "dns_anomaly",
        },
    )
    alert_id = create_resp.json()["id"]
    resp = client.post(f"/alerts/{alert_id}/triage", json={"is_false_positive": True})
    assert resp.status_code == 200
    assert resp.json()["is_false_positive"] is True
    assert resp.json()["status"] == "triaged"


def test_create_alert_invalid_ip(client: TestClient) -> None:
    resp = client.post(
        "/alerts",
        json={
            "title": "Bad Alert",
            "source_ip": "999.0.0.1",
            "criticity": "low",
            "rule_name": "test_rule",
        },
    )
    assert resp.status_code == 422
