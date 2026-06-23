from pathlib import Path

from aro.application.ml.use_cases import (
    TrainAnomalyModelUseCase,
    alerts_to_flows,
    synthesize_baseline,
)
from aro.domain.alerting.entities import Alert
from aro.domain.shared.value_objects import Criticity, IpAddress
from aro.infrastructure.alerting.memory_repo import InMemoryAlertRepository
from aro.infrastructure.ml.anomaly_pipeline import AnomalyPipeline


def test_synthesize_baseline_count_and_shape() -> None:
    flows = synthesize_baseline(5)
    assert len(flows) == 5
    assert all("distinct_dst_ports" in f for f in flows)


def test_alerts_to_flows_uses_port_count() -> None:
    alert = Alert.create(
        title="scan",
        source_ip=IpAddress("203.0.113.7"),
        criticity=Criticity.HIGH,
        rule_name="Nmap Port Scan Detected",
        raw_data={"ports": [1, 2, 3, 4, 5]},
    )
    flows = alerts_to_flows([alert])
    assert flows[0]["distinct_dst_ports"] == 5
    assert flows[0]["source_ip"] == "203.0.113.7"


class _FakeCollector:
    def __init__(self, flows: list[dict]) -> None:
        self._flows = flows

    def capture(self) -> list[dict]:
        return list(self._flows)


def test_train_use_case_produces_report(tmp_path) -> None:
    repo = InMemoryAlertRepository()
    repo.add(
        Alert.create(
            title="scan",
            source_ip=IpAddress("203.0.113.9"),
            criticity=Criticity.CRITICAL,
            rule_name="Nmap Port Scan Detected",
            raw_data={"ports": list(range(1, 80))},
        )
    )
    plot = str(tmp_path / "plot.png")
    use_case = TrainAnomalyModelUseCase(
        collector=_FakeCollector([]),
        pipeline=AnomalyPipeline(),
        repository=repo,
        plot_path=plot,
    )
    report = use_case.execute()
    assert report["trained"] is True
    assert report["augmented"] is True  # peu de flux -> padding
    assert report["plot_url"] == "/ml/plot"
    assert Path(plot).exists()
