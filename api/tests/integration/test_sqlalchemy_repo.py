import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from aro.domain.alerting.entities import Alert
from aro.domain.shared.value_objects import AlertId, AlertStatus, Criticity, IpAddress
from aro.infrastructure.alerting.sqlalchemy_models import Base
from aro.infrastructure.alerting.sqlalchemy_repo import SQLAlchemyAlertRepository


@pytest.fixture()
def session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s
    Base.metadata.drop_all(engine)


@pytest.fixture()
def repo(session: Session) -> SQLAlchemyAlertRepository:
    return SQLAlchemyAlertRepository(session=session)


def _make_alert(**overrides: object) -> Alert:
    defaults: dict[str, object] = dict(
        title="Port Scan",
        source_ip=IpAddress("10.0.0.1"),
        criticity=Criticity.HIGH,
        rule_name="network_port_scan",
    )
    defaults.update(overrides)
    return Alert.create(**defaults)  # type: ignore[arg-type]


def test_add_and_get_by_id(repo: SQLAlchemyAlertRepository) -> None:
    alert = _make_alert()
    repo.add(alert)
    result = repo.get_by_id(alert.id)
    assert result is not None
    assert str(result.id) == str(alert.id)
    assert result.title == alert.title
    assert result.criticity == Criticity.HIGH


def test_get_by_id_not_found(repo: SQLAlchemyAlertRepository) -> None:
    result = repo.get_by_id(AlertId.from_string("00000000-0000-0000-0000-000000000000"))
    assert result is None


def test_list_open_returns_only_open(repo: SQLAlchemyAlertRepository) -> None:
    alert = _make_alert()
    repo.add(alert)
    results = repo.list_open(limit=10, criticity=None)
    assert len(results) == 1
    assert results[0].status == AlertStatus.OPEN


def test_list_open_filtered_by_criticity(repo: SQLAlchemyAlertRepository) -> None:
    repo.add(_make_alert(criticity=Criticity.HIGH))
    repo.add(_make_alert(criticity=Criticity.LOW))
    results = repo.list_open(limit=10, criticity=Criticity.HIGH)
    assert len(results) == 1
    assert results[0].criticity == Criticity.HIGH


def test_list_open_respects_limit(repo: SQLAlchemyAlertRepository) -> None:
    for _ in range(5):
        repo.add(_make_alert())
    results = repo.list_open(limit=3, criticity=None)
    assert len(results) == 3


def test_update_persists_triage(repo: SQLAlchemyAlertRepository) -> None:
    alert = _make_alert()
    repo.add(alert)
    alert.triage(is_false_positive=True)
    repo.update(alert)
    result = repo.get_by_id(alert.id)
    assert result is not None
    assert result.status == AlertStatus.TRIAGED
    assert result.is_false_positive is True


def test_roundtrip_with_destination_ip(repo: SQLAlchemyAlertRepository) -> None:
    alert = _make_alert(destination_ip=IpAddress("172.16.0.1"))
    repo.add(alert)
    result = repo.get_by_id(alert.id)
    assert result is not None
    assert str(result.destination_ip) == "172.16.0.1"
