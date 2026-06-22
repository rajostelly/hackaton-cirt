from fastapi import APIRouter, Depends

from aro.application.integration.use_cases import GetPaloAltoThreatsUseCase
from aro.interfaces.http.dependencies import get_paloalto_threats_use_case
from aro.interfaces.http.schemas.integration import PaloAltoThreatOut

router = APIRouter(prefix="/paloalto", tags=["paloalto"])


@router.get("/threats", response_model=list[PaloAltoThreatOut])
def get_threats(
    limit: int = 50,
    use_case: GetPaloAltoThreatsUseCase = Depends(get_paloalto_threats_use_case),
) -> list[PaloAltoThreatOut]:
    threats = use_case.execute(limit=limit)
    return [
        PaloAltoThreatOut(
            id=t.id,
            threat_name=t.threat_name,
            severity=t.severity,
            action=t.action,
            source_ip=t.source_ip,
            destination_ip=t.destination_ip,
            application=t.application,
            timestamp=t.timestamp,
        )
        for t in threats
    ]
