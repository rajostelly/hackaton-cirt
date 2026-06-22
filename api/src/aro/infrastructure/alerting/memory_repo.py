from aro.domain.alerting.entities import Alert
from aro.domain.shared.value_objects import AlertId, AlertStatus, Criticity


class InMemoryAlertRepository:
    def __init__(self) -> None:
        self._store: dict[str, Alert] = {}

    def add(self, alert: Alert) -> None:
        self._store[str(alert.id)] = alert

    def get_by_id(self, alert_id: AlertId) -> Alert | None:
        return self._store.get(str(alert_id))

    def list_open(self, limit: int = 50, criticity: Criticity | None = None) -> list[Alert]:
        alerts = [a for a in self._store.values() if a.status == AlertStatus.OPEN]
        if criticity is not None:
            alerts = [a for a in alerts if a.criticity == criticity]
        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)[:limit]

    def update(self, alert: Alert) -> None:
        self._store[str(alert.id)] = alert
