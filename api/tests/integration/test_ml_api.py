import pytest
from fastapi.testclient import TestClient

from aro.application.ml.use_cases import TrainAnomalyModelUseCase
from aro.domain.alerting.entities import Alert
from aro.domain.shared.value_objects import Criticity, IpAddress
from aro.infrastructure.alerting.memory_repo import InMemoryAlertRepository
from aro.infrastructure.ml.anomaly_pipeline import AnomalyPipeline
from aro.infrastructure.ml.report_repository import InMemoryMlReportRepository
from aro.interfaces.http.dependencies import (
    get_ml_plot_path,
    get_ml_report_repository,
    get_train_ml_use_case,
)
from aro.main import app


class _FakeCollector:
    def capture(self) -> list[dict]:
        return [
            {
                "source_ip": f"10.0.0.{i}",
                "packets": 10,
                "distinct_dst_ports": 2,
                "distinct_dst_ips": 1,
                "bytes": 1000,
                "syn_count": 1,
            }
            for i in range(1, 11)
        ]


@pytest.fixture()
def client(tmp_path):
    plot = str(tmp_path / "plot.png")
    repo = InMemoryAlertRepository()
    repo.add(
        Alert.create(
            title="scan",
            source_ip=IpAddress("203.0.113.7"),
            criticity=Criticity.HIGH,
            rule_name="Nmap Port Scan Detected",
            raw_data={"ports": list(range(1, 40))},
        )
    )
    use_case = TrainAnomalyModelUseCase(_FakeCollector(), AnomalyPipeline(), repo, plot)
    reports = InMemoryMlReportRepository()
    app.dependency_overrides[get_train_ml_use_case] = lambda: use_case
    app.dependency_overrides[get_ml_plot_path] = lambda: plot
    app.dependency_overrides[get_ml_report_repository] = lambda: reports
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_train_then_report_and_plot(client: TestClient) -> None:
    trained = client.post("/ml/train").json()
    assert trained["trained"] is True
    assert trained["samples"] >= 11
    assert "confusion_matrix" in trained

    report = client.get("/ml/report").json()
    assert report["trained"] is True

    plot_resp = client.get("/ml/plot")
    assert plot_resp.status_code == 200
    assert plot_resp.headers["content-type"] == "image/png"


def test_report_empty_before_training(client: TestClient) -> None:
    assert client.get("/ml/report").json()["trained"] is False
