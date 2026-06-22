import pytest

from aro.domain.alerting.entities import Alert
from aro.domain.shared.value_objects import AlertStatus, Criticity, IpAddress
from aro.infrastructure.alerting.session_repo import SessionScopedAlertRepository
from aro.infrastructure.persistence.database import _normalize_url, init_db, reset_db


@pytest.fixture()
def repo(tmp_path):
    factory = init_db(f"sqlite:///{tmp_path / 'test.db'}")
    yield SessionScopedAlertRepository(factory)
    reset_db()


def _make_alert(**overrides: object) -> Alert:
    defaults: dict[str, object] = dict(
        title="Port Scan",
        source_ip=IpAddress("10.0.0.1"),
        criticity=Criticity.HIGH,
        rule_name="Nmap Port Scan Detected",
    )
    defaults.update(overrides)
    return Alert.create(**defaults)  # type: ignore[arg-type]


def test_normalize_url_forces_psycopg_driver() -> None:
    assert _normalize_url("postgresql://u:p@h/db") == "postgresql+psycopg://u:p@h/db"
    assert _normalize_url("postgres://u:p@h/db") == "postgresql+psycopg://u:p@h/db"
    assert _normalize_url("sqlite:///x.db") == "sqlite:///x.db"


def test_add_and_get_roundtrip(repo: SessionScopedAlertRepository) -> None:
    alert = _make_alert()
    repo.add(alert)
    fetched = repo.get_by_id(alert.id)
    assert fetched is not None
    assert fetched.title == alert.title
    assert fetched.criticity == Criticity.HIGH


def test_list_open_and_filter(repo: SessionScopedAlertRepository) -> None:
    repo.add(_make_alert(criticity=Criticity.HIGH))
    repo.add(_make_alert(criticity=Criticity.LOW))
    assert len(repo.list_open(limit=10, criticity=None)) == 2
    high = repo.list_open(limit=10, criticity=Criticity.HIGH)
    assert len(high) == 1
    assert high[0].criticity == Criticity.HIGH


def test_update_persists_triage(repo: SessionScopedAlertRepository) -> None:
    alert = _make_alert()
    repo.add(alert)
    alert.triage(is_false_positive=True)
    repo.update(alert)
    fetched = repo.get_by_id(alert.id)
    assert fetched is not None
    assert fetched.status == AlertStatus.TRIAGED
    assert fetched.is_false_positive is True


def test_get_repository_uses_database_url(tmp_path, monkeypatch) -> None:
    from aro.interfaces.http.dependencies import get_repository, reset_repository

    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'dep.db'}")
    reset_repository()
    try:
        assert isinstance(get_repository(), SessionScopedAlertRepository)
    finally:
        reset_repository()
        reset_db()
