from __future__ import annotations

from dataclasses import dataclass

from aro.domain.virus.entities import VirusReport
from aro.domain.virus.ports import VirusScanner
from aro.infrastructure.virus.store import VirusStore


@dataclass
class ListVirusUseCase:
    store: VirusStore

    def execute(self) -> list[VirusReport]:
        return self.store.list()


@dataclass
class LookupVirusUseCase:
    scanner: VirusScanner
    store: VirusStore

    def execute(self, indicator: str, kind: str = "ip") -> VirusReport:
        report = self.scanner.scan(indicator, kind)
        self.store.add(report)
        return report
