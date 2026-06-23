from __future__ import annotations

from fastapi import APIRouter, Depends

from aro.application.vulnerability.use_cases import (
    ListVulnerabilitiesUseCase,
    RefreshVulnerabilitiesUseCase,
    VulnerabilityReport,
)
from aro.interfaces.http.dependencies import (
    get_list_vuln_use_case,
    get_refresh_vuln_use_case,
)
from aro.interfaces.http.schemas.vulnerability import VulnerabilityOut, VulnerabilityReportOut

router = APIRouter(prefix="/vulnerabilities", tags=["vulnerabilities"])


def _to_out(report: VulnerabilityReport) -> VulnerabilityReportOut:
    return VulnerabilityReportOut(
        items=[
            VulnerabilityOut(
                cve_id=v.cve_id,
                description=v.description,
                packages=list(v.packages),
                fixed=v.fixed,
                severity=v.severity,
            )
            for v in report.items
        ],
        summary=report.summary,
        last_updated=report.last_updated,
    )


@router.get("", response_model=VulnerabilityReportOut)
def list_vulnerabilities(
    use_case: ListVulnerabilitiesUseCase = Depends(get_list_vuln_use_case),
) -> VulnerabilityReportOut:
    return _to_out(use_case.execute())


@router.post("/scan", response_model=VulnerabilityReportOut)
def scan_vulnerabilities(
    use_case: RefreshVulnerabilitiesUseCase = Depends(get_refresh_vuln_use_case),
) -> VulnerabilityReportOut:
    """Lance `debsecan` sur le serveur et met à jour l'inventaire CVE (lent)."""
    return _to_out(use_case.execute())
