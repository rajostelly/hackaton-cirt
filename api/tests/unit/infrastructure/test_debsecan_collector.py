from aro.domain.shared.value_objects import Criticity
from aro.infrastructure.vulnerability.debsecan_collector import (
    DebsecanCollector,
    parse_debsecan,
)

SAMPLE = """CVE-2026-27456
  util-linux random collection. Allows remote code execution.
  installed: bsdextrautils 2.41-5
             (built from util-linux 2.41-5)
  fixed in unstable: util-linux 2.42-1 (source package)
CVE-2026-3184
  Improper hostname canonicalization leads to privilege escalation.
  installed: bsdextrautils 2.41-5
  installed: bsdutils 2.41-5
CVE-2099-0001
  Minor informational note about logging.
  installed: somepkg 1.0
"""


def test_parse_aggregates_and_classifies() -> None:
    vulns = parse_debsecan(SAMPLE)
    by_id = {v.cve_id: v for v in vulns}
    assert set(by_id) == {"CVE-2026-27456", "CVE-2026-3184", "CVE-2099-0001"}
    assert by_id["CVE-2026-27456"].severity == Criticity.CRITICAL
    assert by_id["CVE-2026-27456"].fixed is True
    assert by_id["CVE-2026-3184"].severity == Criticity.HIGH
    assert by_id["CVE-2026-3184"].fixed is False
    assert by_id["CVE-2026-3184"].packages == ("bsdextrautils", "bsdutils")
    assert by_id["CVE-2099-0001"].severity == Criticity.LOW


def test_parse_sorted_critical_first() -> None:
    vulns = parse_debsecan(SAMPLE)
    assert vulns[0].severity == Criticity.CRITICAL


def test_collector_refresh_populates_cache() -> None:
    collector = DebsecanCollector(runner=lambda suite: SAMPLE, suite="trixie")
    assert collector.cached == []
    assert collector.last_updated is None
    collector.refresh()
    assert len(collector.cached) == 3
    assert collector.last_updated is not None
