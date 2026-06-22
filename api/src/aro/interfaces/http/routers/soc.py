from fastapi import APIRouter, Depends

from aro.application.integration.use_cases import GetSocOverviewUseCase
from aro.interfaces.http.dependencies import get_soc_overview_use_case
from aro.interfaces.http.schemas.integration import SocOverviewOut, SocSourceStatusOut

router = APIRouter(prefix="/soc", tags=["soc"])


@router.get("/overview", response_model=SocOverviewOut)
def overview(
    use_case: GetSocOverviewUseCase = Depends(get_soc_overview_use_case),
) -> SocOverviewOut:
    statuses = use_case.execute()
    return SocOverviewOut(
        sources=[
            SocSourceStatusOut(
                source=s.source,
                online=s.online,
                event_count=s.event_count,
                detail=s.detail,
            )
            for s in statuses
        ]
    )
