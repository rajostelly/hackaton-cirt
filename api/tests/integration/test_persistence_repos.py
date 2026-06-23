from datetime import UTC, datetime

import pytest

from aro.domain.incident.entities import Incident
from aro.domain.incident.value_objects import IncidentType
from aro.domain.shared.value_objects import Criticity
from aro.domain.vulnerability.entities import CveInventory, Vulnerability
from aro.infrastructure.incident.sql_repository import SqlIncidentRepository
from aro.infrastructure.ml.report_repository import SqlMlReportRepository
from aro.infrastructure.persistence.database import init_db, reset_db
from aro.infrastructure.vulnerability.report_repository import SqlCveReportRepository


@pytest.fixture()
def factory(tmp_path):
    f = init_db(f"sqlite:///{tmp_path / 'persist.db'}")
    yield f
    reset_db()


def test_sql_incident_roundtrip(factory) -> None:
    repo = SqlIncidentRepository(factory)
    repo.add(
        Incident(
            id="i1",
            type=IncidentType.TRAFFIC_SPIKE,
            title="Pic",
            description="desc",
            source_ip="192.168.10.5",
            severity=Criticity.HIGH,
            timestamp=datetime.now(UTC),
            details={"total_packets": 900},
        )
    )
    items = repo.list()
    assert len(items) == 1
    assert items[0].id == "i1"
    assert items[0].type == IncidentType.TRAFFIC_SPIKE
    assert items[0].severity == Criticity.HIGH
    assert items[0].details == {"total_packets": 900}


def test_sql_ml_report_latest(factory) -> None:
    repo = SqlMlReportRepository(factory)
    assert repo.latest() is None
    repo.save({"trained": True, "v": 1})
    repo.save({"trained": True, "v": 2})
    latest = repo.latest()
    assert latest is not None
    assert latest["v"] == 2


def test_sql_cve_report_roundtrip(factory) -> None:
    repo = SqlCveReportRepository(factory)
    assert repo.latest() is None
    inv = CveInventory(
        vulnerabilities=[
            Vulnerability("CVE-1", "rce", ("pkg-a", "pkg-b"), True, Criticity.CRITICAL),
            Vulnerability("CVE-2", "note", ("pkg-c",), False, Criticity.LOW),
        ],
        collected_at=datetime.now(UTC),
    )
    repo.save(inv)
    latest = repo.latest()
    assert latest is not None
    assert len(latest.vulnerabilities) == 2
    assert latest.vulnerabilities[0].cve_id == "CVE-1"
    assert latest.vulnerabilities[0].severity == Criticity.CRITICAL
    assert latest.vulnerabilities[0].packages == ("pkg-a", "pkg-b")
