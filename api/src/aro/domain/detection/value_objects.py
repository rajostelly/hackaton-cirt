from __future__ import annotations

from enum import StrEnum


class ScanType(StrEnum):
    """Type de balayage réseau détecté contre l'infrastructure surveillée."""

    PORT_SCAN = "port_scan"
    HTTP_PROBE = "http_probe"
    VULN_SCAN = "vuln_scan"
