from __future__ import annotations

from sqlalchemy.orm import Session

from aro.domain.alerting.entities import Alert
from aro.domain.shared.value_objects import AlertId, AlertStatus, Criticity, IpAddress
from aro.infrastructure.alerting.sqlalchemy_models import AlertModel


class SQLAlchemyAlertRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, alert: Alert) -> None:
        self._session.add(self._to_model(alert))
        self._session.commit()

    def get_by_id(self, alert_id: AlertId) -> Alert | None:
        model = self._session.get(AlertModel, str(alert_id))
        return self._to_domain(model) if model else None

    def list_open(self, limit: int = 50, criticity: Criticity | None = None) -> list[Alert]:
        query = self._session.query(AlertModel).filter(AlertModel.status == "open")
        if criticity is not None:
            query = query.filter(AlertModel.criticity == criticity.value)
        models = query.order_by(AlertModel.timestamp.desc()).limit(limit).all()
        return [self._to_domain(m) for m in models]

    def update(self, alert: Alert) -> None:
        model = self._session.get(AlertModel, str(alert.id))
        if model:
            model.status = str(alert.status)
            model.explanation = alert.explanation
            model.is_false_positive = alert.is_false_positive
            self._session.commit()

    @staticmethod
    def _to_model(alert: Alert) -> AlertModel:
        return AlertModel(
            id=str(alert.id),
            title=alert.title,
            source_ip=str(alert.source_ip),
            destination_ip=str(alert.destination_ip) if alert.destination_ip else None,
            criticity=str(alert.criticity),
            rule_name=alert.rule_name,
            status=str(alert.status),
            timestamp=alert.timestamp,
            explanation=alert.explanation,
            is_false_positive=alert.is_false_positive,
            raw_data=alert.raw_data,
        )

    @staticmethod
    def _to_domain(model: AlertModel) -> Alert:
        return Alert(
            id=AlertId.from_string(model.id),
            title=model.title,
            source_ip=IpAddress(model.source_ip),
            destination_ip=IpAddress(model.destination_ip) if model.destination_ip else None,
            criticity=Criticity(model.criticity),
            rule_name=model.rule_name,
            status=AlertStatus(model.status),
            timestamp=model.timestamp,
            explanation=model.explanation,
            is_false_positive=model.is_false_positive,
            raw_data=model.raw_data,
        )
