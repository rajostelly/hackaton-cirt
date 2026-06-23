from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VirusReport:
    indicator: str          # IP ou hash de fichier
    kind: str               # "ip" | "file"
    malicious: int
    suspicious: int
    harmless: int
    total: int
    label: str | None = None  # étiquette de menace (si connue)

    @property
    def score(self) -> float:
        return round(self.malicious / self.total, 4) if self.total else 0.0

    @property
    def is_malicious(self) -> bool:
        return self.malicious > 0
