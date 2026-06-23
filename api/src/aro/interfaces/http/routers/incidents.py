from __future__ import annotations

from fastapi import APIRouter, Depends

from aro.application.incident.use_cases import (
    AnalyzeIncidentsUseCase,
    ListIncidentsUseCase,
    SimulateIncidentUseCase,
)
from aro.domain.incident.entities import Incident
from aro.interfaces.http.dependencies import (
    get_analyze_incidents_use_case,
    get_list_incidents_use_case,
    get_simulate_incident_use_case,
)
from aro.interfaces.http.schemas.incident import IncidentOut

router = APIRouter(prefix="/incidents", tags=["incidents"])


def _to_out(incident: Incident) -> IncidentOut:
    return IncidentOut(
        id=incident.id,
        type=incident.type,
        title=incident.title,
        description=incident.description,
        source_ip=incident.source_ip,
        severity=incident.severity,
        timestamp=incident.timestamp,
        details=incident.details,
    )


@router.get("", response_model=list[IncidentOut])
def list_incidents(
    use_case: ListIncidentsUseCase = Depends(get_list_incidents_use_case),
) -> list[IncidentOut]:
    return [_to_out(i) for i in use_case.execute()]


@router.post("/analyze", response_model=list[IncidentOut])
def analyze_incidents(
    use_case: AnalyzeIncidentsUseCase = Depends(get_analyze_incidents_use_case),
    lister: ListIncidentsUseCase = Depends(get_list_incidents_use_case),
) -> list[IncidentOut]:
    """Capture le réseau (tshark) et analyse les anomalies (pic, déplacement latéral)."""
    use_case.execute()
    return [_to_out(i) for i in lister.execute()]


@router.post("/simulate", response_model=list[IncidentOut])
def simulate_incidents(
    use_case: SimulateIncidentUseCase = Depends(get_simulate_incident_use_case),
    lister: ListIncidentsUseCase = Depends(get_list_incidents_use_case),
) -> list[IncidentOut]:
    """Injecte des incidents d'exemple réalistes (démonstration)."""
    use_case.execute()
    return [_to_out(i) for i in lister.execute()]
