from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class MlReportOut(BaseModel):
    trained: bool
    samples: int = 0
    anomalies_count: int = 0
    confusion_matrix: dict[str, int] = Field(default_factory=dict)
    metrics: dict[str, float] = Field(default_factory=dict)
    anomalies: list[dict[str, Any]] = Field(default_factory=list)
    augmented: bool = False
    plot_url: str | None = None
    generated_at: str | None = None
