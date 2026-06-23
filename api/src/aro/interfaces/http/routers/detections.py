from __future__ import annotations

import os

from fastapi import APIRouter, BackgroundTasks, Depends

from aro.application.alerting.use_cases import to_output
from aro.application.detection.dto import ScanDetectionInput
from aro.application.detection.use_cases import RecordScanDetectionUseCase
from aro.domain.alerting.ports import AlertExplainer, AlertRepository
from aro.domain.shared.value_objects import AlertId
from aro.infrastructure.alerting.static_explainer import DEFAULT_EXPLANATION
from aro.infrastructure.realtime.broker import AlertBroker
from aro.interfaces.http import mappers
from aro.interfaces.http.dependencies import (
    auto_block,
    get_broker,
    get_explainer,
    get_record_scan_use_case,
    get_repository,
)
from aro.interfaces.http.schemas.alerts import AlertOut
from aro.interfaces.http.schemas.detection import ScanDetectionIn

router = APIRouter(prefix="/detections", tags=["detections"])


def _to_input(payload: ScanDetectionIn) -> ScanDetectionInput:
    return ScanDetectionInput(
        source_ip=payload.source_ip,
        scan_type=payload.scan_type,
        ports=payload.ports,
        target=payload.target,
        packet_count=payload.packet_count,
        detail=payload.detail,
    )


def enrich_with_ai(
    alert_id: str,
    repo: AlertRepository,
    explainer: AlertExplainer,
    broker: AlertBroker,
) -> None:
    """Tâche de fond : attache l'explication IA puis re-pousse l'alerte en SSE.

    Tolérante aux pannes : sans clé Groq (ou en cas d'erreur réseau), on garde
    l'explication de repli déjà disponible.
    """
    alert = repo.get_by_id(AlertId.from_string(alert_id))
    if alert is None:
        return
    explanation = DEFAULT_EXPLANATION
    if os.environ.get("GROQ_API_KEY"):
        try:
            explanation = explainer.explain(alert) or DEFAULT_EXPLANATION
        except Exception:  # noqa: BLE001 - l'IA ne doit jamais casser l'alerte
            explanation = DEFAULT_EXPLANATION
    alert.attach_explanation(explanation)
    repo.update(alert)
    broker.publish("alert.updated", mappers.to_alert_out(to_output(alert)).model_dump(mode="json"))


@router.post("/scan", response_model=AlertOut, status_code=201)
def report_scan(
    payload: ScanDetectionIn,
    background: BackgroundTasks,
    use_case: RecordScanDetectionUseCase = Depends(get_record_scan_use_case),
    repo: AlertRepository = Depends(get_repository),
    explainer: AlertExplainer = Depends(get_explainer),
    broker: AlertBroker = Depends(get_broker),
) -> AlertOut:
    """Point d'entrée du capteur : un balayage détecté → alerte + push temps réel."""
    result = use_case.execute(_to_input(payload))
    out = mappers.to_alert_out(result)
    broker.publish("alert.created", out.model_dump(mode="json"))
    auto_block(out.source_ip)  # blocage pare-feu automatique si mode IPS
    background.add_task(enrich_with_ai, result.id, repo, explainer, broker)
    return out
