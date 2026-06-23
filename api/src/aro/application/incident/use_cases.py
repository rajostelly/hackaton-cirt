from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from aro.domain.incident.entities import Incident
from aro.domain.incident.ports import IncidentRepository
from aro.domain.incident.services import detect_lateral_movement, detect_traffic_spike
from aro.domain.incident.value_objects import IncidentType
from aro.domain.shared.value_objects import Criticity
from aro.infrastructure.incident.tshark_incident_collector import TsharkIncidentCollector


def _now() -> datetime:
    return datetime.now(UTC)


def _spike_incident(total_packets: int, threshold: int) -> Incident:
    severity = Criticity.HIGH if total_packets >= threshold * 3 else Criticity.MEDIUM
    return Incident(
        id=str(uuid.uuid4()),
        type=IncidentType.TRAFFIC_SPIKE,
        title="Pic de trafic réseau anormal",
        description=(
            f"{total_packets} paquets observés sur la fenêtre de capture "
            f"(seuil d'alerte : {threshold}). Possible saturation, exfiltration "
            "de données ou attaque par déni de service."
        ),
        source_ip="—",
        severity=severity,
        timestamp=_now(),
        details={"total_packets": total_packets, "threshold": threshold},
    )


def _lateral_incident(finding: dict) -> Incident:
    targets = ", ".join(finding["target_segments"])
    return Incident(
        id=str(uuid.uuid4()),
        type=IncidentType.LATERAL_MOVEMENT,
        title="Déplacement latéral entre segments réseau",
        description=(
            f"La machine {finding['source_ip']} (segment {finding['src_segment']}) "
            f"ouvre des connexions vers d'autres segments internes ({targets}). "
            "Comportement typique d'une propagation après compromission."
        ),
        source_ip=finding["source_ip"],
        severity=Criticity.HIGH,
        timestamp=_now(),
        details=finding,
    )


@dataclass
class AnalyzeIncidentsUseCase:
    collector: TsharkIncidentCollector
    store: IncidentRepository
    spike_threshold: int = 500

    def execute(self) -> list[Incident]:
        flows, total = self.collector.capture()
        incidents: list[Incident] = []
        if detect_traffic_spike(total, self.spike_threshold):
            incidents.append(_spike_incident(total, self.spike_threshold))
        for finding in detect_lateral_movement(flows):
            incidents.append(_lateral_incident(finding))
        for incident in incidents:
            self.store.add(incident)
        return incidents


@dataclass
class ListIncidentsUseCase:
    store: IncidentRepository

    def execute(self, limit: int = 100) -> list[Incident]:
        return self.store.list(limit=limit)


@dataclass
class SimulateIncidentUseCase:
    """Injecte des incidents d'exemple réalistes (démo sans trafic réel)."""

    store: IncidentRepository

    def execute(self) -> list[Incident]:
        incidents = [
            _lateral_incident(
                {
                    "source_ip": "192.168.10.42",
                    "src_segment": "192.168.10",
                    "target_segments": ["192.168.20", "192.168.30"],
                }
            ),
            _spike_incident(total_packets=4200, threshold=500),
        ]
        for incident in incidents:
            self.store.add(incident)
        return incidents
