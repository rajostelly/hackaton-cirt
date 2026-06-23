import pytest
from fastapi.testclient import TestClient

from aro.application.vulnerability.use_cases import (
    ListVulnerabilitiesUseCase,
    RefreshVulnerabilitiesUseCase,
)
from aro.infrastructure.vulnerability.debsecan_collector import DebsecanCollector
from aro.infrastructure.vulnerability.report_repository import InMemoryCveReportRepository
from aro.interfaces.http.dependencies import (
    get_list_vuln_use_case,
    get_refresh_vuln_use_case,
)
from aro.main import app

SAMPLE = """CVE-2026-27456
  Allows remote code execution.
  installed: bsdextrautils 2.41-5
  fixed in unstable: util-linux 2.42-1 (source package)
CVE-2026-3184
  Local privilege escalation.
  installed: bsdutils 2.41-5
CVE-2099-0001
  Minor note.
  installed: somepkg 1.0
"""


@pytest.fixture()
def client() -> TestClient:
    collector = DebsecanCollector(runner=lambda suite: SAMPLE, suite="trixie")
    repo = InMemoryCveReportRepository()
    app.dependency_overrides[get_list_vuln_use_case] = lambda: ListVulnerabilitiesUseCase(repo)
    app.dependency_overrides[get_refresh_vuln_use_case] = lambda: RefreshVulnerabilitiesUseCase(
        collector, repo
    )
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_list_empty_before_scan(client: TestClient) -> None:
    data = client.get("/vulnerabilities").json()
    assert data["summary"]["total"] == 0
    assert data["items"] == []


def test_scan_then_summary(client: TestClient) -> None:
    data = client.post("/vulnerabilities/scan").json()
    assert data["summary"]["total"] == 3
    assert data["summary"]["critical"] == 1
    assert data["summary"]["high"] == 1
    assert data["summary"]["low"] == 1
    assert data["items"][0]["severity"] == "critical"
    # le cache persiste pour le GET suivant
    assert client.get("/vulnerabilities").json()["summary"]["total"] == 3
