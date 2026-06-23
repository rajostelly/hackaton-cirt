from aro.application.virus.use_cases import ListVirusUseCase, LookupVirusUseCase
from aro.domain.virus.entities import VirusReport
from aro.infrastructure.virus.store import VirusStore


def test_store_has_default_seed() -> None:
    assert len(VirusStore().list()) >= 3


def test_list_use_case_returns_seed() -> None:
    assert len(ListVirusUseCase(VirusStore()).execute()) >= 3


class _FakeScanner:
    def scan(self, indicator: str, kind: str) -> VirusReport:
        return VirusReport(indicator, kind, malicious=5, suspicious=0, harmless=60, total=65)


def test_lookup_adds_to_store() -> None:
    store = VirusStore(seed=[])
    report = LookupVirusUseCase(_FakeScanner(), store).execute("203.0.113.9", "ip")
    assert report.is_malicious is True
    assert any(r.indicator == "203.0.113.9" for r in store.list())
