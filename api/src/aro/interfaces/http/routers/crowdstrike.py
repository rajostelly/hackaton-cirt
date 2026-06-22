from fastapi import APIRouter, Depends

from aro.application.integration.use_cases import GetCrowdStrikeDetectionsUseCase
from aro.interfaces.http.dependencies import get_crowdstrike_detections_use_case
from aro.interfaces.http.schemas.integration import CrowdStrikeDetectionOut

router = APIRouter(prefix="/crowdstrike", tags=["crowdstrike"])


@router.get("/detections", response_model=list[CrowdStrikeDetectionOut])
def get_detections(
    limit: int = 50,
    use_case: GetCrowdStrikeDetectionsUseCase = Depends(get_crowdstrike_detections_use_case),
) -> list[CrowdStrikeDetectionOut]:
    detections = use_case.execute(limit=limit)
    return [
        CrowdStrikeDetectionOut(
            id=d.id,
            detection_name=d.detection_name,
            severity=d.severity,
            tactic=d.tactic,
            technique=d.technique,
            hostname=d.hostname,
            status=d.status,
            timestamp=d.timestamp,
        )
        for d in detections
    ]
