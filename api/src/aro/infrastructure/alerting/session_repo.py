from __future__ import annotations

from sqlalchemy.orm import Session, sessionmaker

from aro.domain.alerting.entities import Alert
from aro.domain.shared.value_objects import AlertId, Criticity
from aro.infrastructure.alerting.sqlalchemy_repo import SQLAlchemyAlertRepository


class SessionScopedAlertRepository:
    """Repository sans état : ouvre une session par opération via la factory.

    Sûr à partager comme singleton (requêtes HTTP + tâches de fond), contrairement
    à `SQLAlchemyAlertRepository` qui est lié à une session unique.
    """

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def add(self, alert: Alert) -> None:
        with self._session_factory() as session:
            SQLAlchemyAlertRepository(session).add(alert)

    def get_by_id(self, alert_id: AlertId) -> Alert | None:
        with self._session_factory() as session:
            return SQLAlchemyAlertRepository(session).get_by_id(alert_id)

    def list_open(self, limit: int = 50, criticity: Criticity | None = None) -> list[Alert]:
        with self._session_factory() as session:
            return SQLAlchemyAlertRepository(session).list_open(limit=limit, criticity=criticity)

    def update(self, alert: Alert) -> None:
        with self._session_factory() as session:
            SQLAlchemyAlertRepository(session).update(alert)
