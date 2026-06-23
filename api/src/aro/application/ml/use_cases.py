from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from aro.domain.alerting.ports import AlertRepository
from aro.infrastructure.ml.anomaly_pipeline import AnomalyPipeline
from aro.infrastructure.ml.tshark_collector import TsharkCollector

# Nombre minimal d'échantillons pour entraîner un modèle exploitable.
MIN_SAMPLES = 12


def synthesize_baseline(n: int, seed: int = 7) -> list[dict[str, Any]]:
    """Trafic normal synthétique (padding déterministe quand la capture est maigre)."""
    rng = random.Random(seed)
    return [
        {
            "source_ip": f"10.0.0.{i + 1}",
            "packets": rng.randint(5, 40),
            "distinct_dst_ports": rng.randint(1, 4),
            "distinct_dst_ips": rng.randint(1, 3),
            "bytes": rng.randint(500, 8000),
            "syn_count": rng.randint(0, 3),
        }
        for i in range(n)
    ]


def synthesize_scans(n: int = 2) -> list[dict[str, Any]]:
    """Exemplaires de scans (anomalies nettes) pour la démonstration du modèle."""
    return [
        {
            "source_ip": f"198.51.100.{i + 1}",
            "packets": 150 + i * 80,
            "distinct_dst_ports": 80 + i * 120,
            "distinct_dst_ips": 1,
            "bytes": (80 + i * 120) * 60,
            "syn_count": 80 + i * 120,
        }
        for i in range(n)
    ]


def alerts_to_flows(alerts: list[Any]) -> list[dict[str, Any]]:
    """Convertit les attaques détectées (capteur) en flux anormaux pour l'entraînement."""
    flows = []
    for alert in alerts:
        raw = alert.raw_data or {}
        ports = raw.get("ports") or []
        n_ports = len(ports) if ports else (50 if "scan" in alert.rule_name.lower() else 1)
        flows.append(
            {
                "source_ip": str(alert.source_ip),
                "packets": raw.get("packet_count") or n_ports or 1,
                "distinct_dst_ports": n_ports,
                "distinct_dst_ips": 1,
                "bytes": (n_ports or 1) * 60,
                "syn_count": n_ports or 1,
            }
        )
    return flows


@dataclass
class TrainAnomalyModelUseCase:
    collector: TsharkCollector
    pipeline: AnomalyPipeline
    repository: AlertRepository
    plot_path: str

    def execute(self) -> dict[str, Any]:
        # 1. collecte : flux réseau réels (tshark) + attaques détectées (capteur)
        flows = self.collector.capture()
        flows += alerts_to_flows(self.repository.list_open(limit=200, criticity=None))
        augmented = False
        if len(flows) < MIN_SAMPLES:
            # Mode démonstration : on complète avec du trafic normal + des
            # exemplaires de scans pour que le modèle ait les deux classes.
            flows += synthesize_baseline(MIN_SAMPLES - len(flows))
            flows += synthesize_scans(2)
            augmented = True

        report = self.pipeline.run(flows, self.plot_path)
        report["augmented"] = augmented
        report["plot_url"] = "/ml/plot"
        report["generated_at"] = datetime.now(UTC).isoformat()
        return report
