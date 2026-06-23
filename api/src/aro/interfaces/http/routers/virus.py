from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from aro.application.virus.use_cases import ListVirusUseCase, LookupVirusUseCase
from aro.domain.virus.entities import VirusReport
from aro.interfaces.http.dependencies import (
    get_list_virus_use_case,
    get_lookup_virus_use_case,
)
from aro.interfaces.http.schemas.virus import VirusLookupIn, VirusReportOut

router = APIRouter(prefix="/virus", tags=["virus"])


def _to_out(report: VirusReport) -> VirusReportOut:
    return VirusReportOut(
        indicator=report.indicator,
        kind=report.kind,
        malicious=report.malicious,
        suspicious=report.suspicious,
        harmless=report.harmless,
        total=report.total,
        label=report.label,
        score=report.score,
        is_malicious=report.is_malicious,
    )


@router.get("", response_model=list[VirusReportOut])
def list_virus(
    use_case: ListVirusUseCase = Depends(get_list_virus_use_case),
) -> list[VirusReportOut]:
    return [_to_out(r) for r in use_case.execute()]


@router.post("/lookup", response_model=VirusReportOut)
def lookup_virus(
    payload: VirusLookupIn,
    use_case: LookupVirusUseCase = Depends(get_lookup_virus_use_case),
) -> VirusReportOut:
    """Interroge VirusTotal pour une IP ou un hash de fichier."""
    try:
        report = use_case.execute(payload.indicator, payload.kind)
    except Exception as exc:  # noqa: BLE001 - clé manquante / erreur réseau VT
        raise HTTPException(status_code=502, detail=f"VirusTotal indisponible: {exc}") from exc
    return _to_out(report)
