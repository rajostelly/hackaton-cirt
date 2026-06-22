class AlertNotFound(Exception):
    def __init__(self, alert_id: str) -> None:
        super().__init__(f"alerte non trouvée: {alert_id}")
