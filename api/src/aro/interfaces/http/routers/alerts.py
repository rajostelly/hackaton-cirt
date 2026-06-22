from __future__ import annotations

from fastapi import APIRouter, Depends

from aro.domain.shared.value_objects import Criticity
from aro.interfaces.http import mappers
from aro.interfaces.http.dependencies import (
    get_get_use_case,
    get_ingest_use_case,
    get_list_use_case,
    get_triage_use_case,
)
from aro.interfaces.http.schemas.alerts import AlertIn, AlertOut, TriageIn

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertOut])
def list_open_alerts(
    limit: int = 50,
    criticity: Criticity | None = None,
    use_case=Depends(get_list_use_case),
) -> list[AlertOut]:
    results = use_case.execute(limit=limit, criticity=criticity)
    return [mappers.to_alert_out(r) for r in results]


@router.post("", response_model=AlertOut, status_code=201)
def ingest_alert(
    payload: AlertIn,
    use_case=Depends(get_ingest_use_case),
) -> AlertOut:
    result = use_case.execute(mappers.to_ingest_input(payload))
    return mappers.to_alert_out(result)


@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(
    alert_id: str,
    use_case=Depends(get_get_use_case),
) -> AlertOut:
    result = use_case.execute(alert_id)
    return mappers.to_alert_out(result)


@router.post("/{alert_id}/triage", response_model=AlertOut)
def triage_alert(
    alert_id: str,
    payload: TriageIn,
    use_case=Depends(get_triage_use_case),
) -> AlertOut:
    result = use_case.execute(mappers.to_triage_input(alert_id, payload))
    return mappers.to_alert_out(result)
