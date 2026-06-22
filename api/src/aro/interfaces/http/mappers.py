from aro.application.alerting.dto import AlertOutput, IngestAlertInput, TriageAlertInput
from aro.interfaces.http.schemas.alerts import AlertIn, AlertOut, TriageIn


def to_ingest_input(schema: AlertIn) -> IngestAlertInput:
    return IngestAlertInput(
        title=schema.title,
        source_ip=schema.source_ip,
        criticity=schema.criticity,
        rule_name=schema.rule_name,
        destination_ip=schema.destination_ip,
        raw_data=schema.raw_data,
    )


def to_triage_input(alert_id: str, schema: TriageIn) -> TriageAlertInput:
    return TriageAlertInput(
        alert_id=alert_id,
        is_false_positive=schema.is_false_positive,
        analyst_note=schema.analyst_note,
    )


def to_alert_out(dto: AlertOutput) -> AlertOut:
    return AlertOut(
        id=dto.id,
        title=dto.title,
        source_ip=dto.source_ip,
        destination_ip=dto.destination_ip,
        criticity=dto.criticity,
        rule_name=dto.rule_name,
        status=dto.status,
        timestamp=dto.timestamp,
        explanation=dto.explanation,
        is_false_positive=dto.is_false_positive,
    )
