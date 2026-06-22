from __future__ import annotations

from dataclasses import dataclass

from aro.domain.alerting.entities import Alert
from aro.domain.alerting.exceptions import AlertNotFound
from aro.domain.alerting.ports import AlertExplainer, AlertRepository
from aro.domain.shared.value_objects import AlertId, Criticity, IpAddress
from aro.application.alerting.dto import AlertOutput, IngestAlertInput, TriageAlertInput


def _to_output(alert: Alert) -> AlertOutput:
    return AlertOutput(
        id=str(alert.id),
        title=alert.title,
        source_ip=str(alert.source_ip),
        criticity=alert.criticity,
        rule_name=alert.rule_name,
        status=alert.status,
        timestamp=alert.timestamp,
        destination_ip=str(alert.destination_ip) if alert.destination_ip else None,
        explanation=alert.explanation,
        is_false_positive=alert.is_false_positive,
    )


@dataclass
class IngestAlertUseCase:
    repository: AlertRepository
    explainer: AlertExplainer

    def execute(self, data: IngestAlertInput) -> AlertOutput:
        alert = Alert.create(
            title=data.title,
            source_ip=IpAddress(data.source_ip),
            criticity=data.criticity,
            rule_name=data.rule_name,
            destination_ip=IpAddress(data.destination_ip) if data.destination_ip else None,
            raw_data=data.raw_data,
        )
        alert.attach_explanation(self.explainer.explain(alert))
        self.repository.add(alert)
        return _to_output(alert)


@dataclass
class ListOpenAlertsUseCase:
    repository: AlertRepository

    def execute(self, limit: int = 50, criticity: Criticity | None = None) -> list[AlertOutput]:
        alerts = self.repository.list_open(limit=limit, criticity=criticity)
        return [_to_output(a) for a in alerts]


@dataclass
class GetAlertUseCase:
    repository: AlertRepository

    def execute(self, alert_id: str) -> AlertOutput:
        aid = AlertId.from_string(alert_id)
        alert = self.repository.get_by_id(aid)
        if alert is None:
            raise AlertNotFound(alert_id)
        return _to_output(alert)


@dataclass
class TriageAlertUseCase:
    repository: AlertRepository

    def execute(self, data: TriageAlertInput) -> AlertOutput:
        aid = AlertId.from_string(data.alert_id)
        alert = self.repository.get_by_id(aid)
        if alert is None:
            raise AlertNotFound(data.alert_id)
        alert.triage(data.is_false_positive)
        self.repository.update(alert)
        return _to_output(alert)
