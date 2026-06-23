from __future__ import annotations

from typing import Protocol

from aro.domain.virus.entities import VirusReport


class VirusScanner(Protocol):
    def scan(self, indicator: str, kind: str) -> VirusReport: ...
