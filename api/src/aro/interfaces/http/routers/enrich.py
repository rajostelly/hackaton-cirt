from fastapi import APIRouter, Depends

from aro.application.integration.use_cases import EnrichAlertWithVirusTotalUseCase
from aro.interfaces.http.dependencies import get_enrich_use_case
from aro.interfaces.http.schemas.integration import ThreatReportOut

router = APIRouter(prefix="/alerts", tags=["enrich"])


@router.get("/{alert_id}/enrich", response_model=ThreatReportOut)
def enrich_alert(
    alert_id: str,
    use_case: EnrichAlertWithVirusTotalUseCase = Depends(get_enrich_use_case),
) -> ThreatReportOut:
    report = use_case.execute(alert_id)
    return ThreatReportOut(
        ip=report.ip,
        malicious_count=report.malicious_count,
        suspicious_count=report.suspicious_count,
        harmless_count=report.harmless_count,
        total_engines=report.total_engines,
        is_malicious=report.is_malicious,
        threat_score=report.threat_score,
    )
