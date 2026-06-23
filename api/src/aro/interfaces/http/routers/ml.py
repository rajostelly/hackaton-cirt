from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from aro.infrastructure.ml.report_repository import MlReportRepository
from aro.interfaces.http.dependencies import (
    get_ml_plot_path,
    get_ml_report_repository,
    get_train_ml_use_case,
)
from aro.interfaces.http.schemas.ml import MlReportOut

router = APIRouter(prefix="/ml", tags=["ml"])


@router.post("/train", response_model=MlReportOut)
def train(
    use_case: Any = Depends(get_train_ml_use_case),
    reports: MlReportRepository = Depends(get_ml_report_repository),
) -> dict:
    """Capture le réseau (tshark) + attaques détectées, entraîne l'Isolation Forest."""
    report = use_case.execute()
    reports.save(report)  # persisté (survit aux redémarrages si DATABASE_URL)
    return report


@router.get("/report", response_model=MlReportOut)
def report(reports: MlReportRepository = Depends(get_ml_report_repository)) -> dict:
    return reports.latest() or {"trained": False}


@router.get("/plot")
def plot(plot_path: str = Depends(get_ml_plot_path)) -> FileResponse:
    if not Path(plot_path).exists():
        raise HTTPException(status_code=404, detail="Aucun graphique généré")
    return FileResponse(plot_path, media_type="image/png")
