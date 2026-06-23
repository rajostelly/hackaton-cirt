from __future__ import annotations

from enum import StrEnum


class IncidentType(StrEnum):
    """Type d'incident réseau détecté par l'agent d'analyse (tshark)."""

    TRAFFIC_SPIKE = "traffic_spike"        # pic anormal de trafic
    LATERAL_MOVEMENT = "lateral_movement"  # un segment qui parle à d'autres segments
