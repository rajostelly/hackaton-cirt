from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Protocol

from sqlalchemy.orm import Session, sessionmaker

from aro.infrastructure.persistence.models import MlReportModel


class MlReportRepository(Protocol):
    def save(self, report: dict[str, Any]) -> None: ...
    def latest(self) -> dict[str, Any] | None: ...


class InMemoryMlReportRepository:
    def __init__(self) -> None:
        self._latest: dict[str, Any] | None = None

    def save(self, report: dict[str, Any]) -> None:
        self._latest = report

    def latest(self) -> dict[str, Any] | None:
        return self._latest


class SqlMlReportRepository:
    """Historise les rapports ML ; `latest()` renvoie le plus récent."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def save(self, report: dict[str, Any]) -> None:
        with self._session_factory() as session:
            session.add(MlReportModel(report=report, created_at=datetime.now(UTC)))
            session.commit()

    def latest(self) -> dict[str, Any] | None:
        with self._session_factory() as session:
            row = session.query(MlReportModel).order_by(MlReportModel.id.desc()).first()
            return dict(row.report) if row else None
