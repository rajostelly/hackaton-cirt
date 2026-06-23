from __future__ import annotations

from aro.domain.virus.entities import VirusReport

# Données par défaut : indicateurs malveillants connus (exemples pédagogiques),
# pour que la page ne soit pas vide avant toute recherche VirusTotal.
DEFAULT_SEED: list[VirusReport] = [
    VirusReport(
        indicator="44d88612fea8a8f36de82e1278abb02f",
        kind="file",
        malicious=63,
        suspicious=0,
        harmless=5,
        total=68,
        label="EICAR-Test-File (signature de test antivirus)",
    ),
    VirusReport(
        indicator="185.220.101.1",
        kind="ip",
        malicious=14,
        suspicious=3,
        harmless=40,
        total=57,
        label="Nœud de sortie Tor / activité malveillante",
    ),
    VirusReport(
        indicator="45.155.205.233",
        kind="ip",
        malicious=9,
        suspicious=2,
        harmless=46,
        total=57,
        label="Scanner / force brute connu",
    ),
]


class VirusStore:
    def __init__(self, seed: list[VirusReport] | None = None) -> None:
        items = DEFAULT_SEED if seed is None else seed
        self._items: dict[str, VirusReport] = {r.indicator: r for r in items}

    def add(self, report: VirusReport) -> None:
        self._items[report.indicator] = report

    def list(self) -> list[VirusReport]:
        return sorted(self._items.values(), key=lambda r: (-r.malicious, r.indicator))
