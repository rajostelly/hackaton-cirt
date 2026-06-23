from __future__ import annotations

from sqlalchemy.orm import Session, sessionmaker

from aro.domain.incident.entities import Incident
from aro.domain.incident.value_objects import IncidentType
from aro.domain.shared.value_objects import Criticity
from aro.infrastructure.persistence.models import IncidentModel


class SqlIncidentRepository:
    """Repository d'incidents persisté en base (une session par opération)."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def add(self, incident: Incident) -> None:
        with self._session_factory() as session:
            session.add(
                IncidentModel(
                    id=incident.id,
                    type=str(incident.type),
                    title=incident.title,
                    description=incident.description,
                    source_ip=incident.source_ip,
                    severity=str(incident.severity),
                    timestamp=incident.timestamp,
                    details=incident.details,
                )
            )
            session.commit()

    def list(self, limit: int = 100) -> list[Incident]:
        with self._session_factory() as session:
            rows = (
                session.query(IncidentModel)
                .order_by(IncidentModel.timestamp.desc())
                .limit(limit)
                .all()
            )
            return [
                Incident(
                    id=row.id,
                    type=IncidentType(row.type),
                    title=row.title,
                    description=row.description,
                    source_ip=row.source_ip,
                    severity=Criticity(row.severity),
                    timestamp=row.timestamp,
                    details=row.details or {},
                )
                for row in rows
            ]
