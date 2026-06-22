from aro.domain.alerting.entities import Alert
from aro.domain.shared.value_objects import AlertStatus, Criticity, IpAddress


def _make_alert(**overrides: object) -> Alert:
    defaults: dict[str, object] = dict(
        title="Port Scan Detected",
        source_ip=IpAddress("10.0.0.1"),
        criticity=Criticity.HIGH,
        rule_name="network_port_scan",
    )
    defaults.update(overrides)
    return Alert.create(**defaults)  # type: ignore[arg-type]


def test_new_alert_has_open_status() -> None:
    alert = _make_alert()
    assert alert.status == AlertStatus.OPEN


def test_new_alert_has_no_explanation() -> None:
    alert = _make_alert()
    assert alert.explanation is None


def test_attach_explanation() -> None:
    alert = _make_alert()
    alert.attach_explanation("Scan de ports détecté depuis un hôte interne.")
    assert alert.explanation == "Scan de ports détecté depuis un hôte interne."


def test_triage_as_false_positive() -> None:
    alert = _make_alert()
    alert.triage(is_false_positive=True)
    assert alert.is_false_positive is True
    assert alert.status == AlertStatus.TRIAGED


def test_triage_as_true_positive() -> None:
    alert = _make_alert()
    alert.triage(is_false_positive=False)
    assert alert.is_false_positive is False
    assert alert.status == AlertStatus.TRIAGED


def test_domain_service_criticity_classify() -> None:
    from aro.domain.alerting.services import CriticityPolicy

    policy = CriticityPolicy()
    assert policy.classify(95) == Criticity.CRITICAL
    assert policy.classify(80) == Criticity.HIGH
    assert policy.classify(60) == Criticity.MEDIUM
    assert policy.classify(10) == Criticity.LOW
