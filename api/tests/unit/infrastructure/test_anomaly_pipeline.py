from pathlib import Path

from aro.infrastructure.ml.anomaly_pipeline import AnomalyPipeline
from aro.infrastructure.ml.tshark_collector import parse_flows


def _normal(i: int) -> dict:
    return {
        "source_ip": f"10.0.0.{i}",
        "packets": 10 + i,
        "distinct_dst_ports": 2,
        "distinct_dst_ips": 1,
        "bytes": 1000 + i * 10,
        "syn_count": 1,
    }


def _scan(ip: str, ports: int) -> dict:
    return {
        "source_ip": ip,
        "packets": ports,
        "distinct_dst_ports": ports,
        "distinct_dst_ips": 1,
        "bytes": ports * 60,
        "syn_count": ports,
    }


def test_pipeline_detects_scan_anomaly(tmp_path) -> None:
    flows = [_normal(i) for i in range(1, 11)] + [_scan("203.0.113.7", 60)]
    plot = str(tmp_path / "plot.png")
    report = AnomalyPipeline().run(flows, plot)

    assert report["trained"] is True
    assert report["samples"] == 11
    assert set(report["confusion_matrix"]) == {"tn", "fp", "fn", "tp"}
    assert set(report["metrics"]) == {"precision", "recall", "accuracy"}
    assert report["anomalies_count"] >= 1
    assert Path(plot).exists()


def test_pipeline_scan_severity_and_not_novel(tmp_path) -> None:
    flows = [_normal(i) for i in range(1, 11)] + [_scan("203.0.113.8", 120)]
    report = AnomalyPipeline().run(flows, str(tmp_path / "p.png"))
    scan_anomalies = [a for a in report["anomalies"] if a["distinct_dst_ports"] >= 100]
    assert scan_anomalies, "le scan large doit être détecté"
    assert scan_anomalies[0]["severity"] == "critical"
    assert scan_anomalies[0]["is_novel"] is False


def test_pipeline_empty_not_trained(tmp_path) -> None:
    report = AnomalyPipeline().run([], str(tmp_path / "p.png"))
    assert report["trained"] is False


def test_parse_flows_aggregates_per_source() -> None:
    csv = "\n".join(
        [
            "203.0.113.7,10.0.0.1,22,60,1",
            "203.0.113.7,10.0.0.1,80,60,1",
            "203.0.113.7,10.0.0.1,443,60,1",
            "10.0.0.5,10.0.0.1,443,500,0",
        ]
    )
    flows = {f["source_ip"]: f for f in parse_flows(csv)}
    assert flows["203.0.113.7"]["distinct_dst_ports"] == 3
    assert flows["203.0.113.7"]["syn_count"] == 3
    assert flows["10.0.0.5"]["packets"] == 1
