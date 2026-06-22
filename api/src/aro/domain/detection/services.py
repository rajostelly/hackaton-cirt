from __future__ import annotations

from aro.domain.detection.value_objects import ScanType
from aro.domain.shared.value_objects import Criticity

# Seuils (nombre de ports distincts touchés) pour classer un scan de ports.
PORT_SCAN_CRITICAL = 100
PORT_SCAN_HIGH = 20
PORT_SCAN_MEDIUM = 5


def classify_scan(scan_type: ScanType, port_count: int) -> Criticity:
    """Politique de criticité : plus le balayage est large, plus c'est grave.

    Un sondage HTTP ou un scan de vulnérabilités (NSE) est intentionnel et
    ciblé : il est traité d'emblée comme élevé.
    """
    if scan_type in (ScanType.HTTP_PROBE, ScanType.VULN_SCAN):
        return Criticity.HIGH
    if port_count >= PORT_SCAN_CRITICAL:
        return Criticity.CRITICAL
    if port_count >= PORT_SCAN_HIGH:
        return Criticity.HIGH
    if port_count >= PORT_SCAN_MEDIUM:
        return Criticity.MEDIUM
    return Criticity.LOW


# Marqueurs d'agents utilisateurs typiques d'un sondage/scan nmap côté HTTP
# (scripts NSE http-*, -sV). On reste volontairement centré sur nmap.
_HTTP_SCANNER_MARKERS = ("nmap", "nmap scripting engine")


def is_nmap_http_probe(user_agent: str) -> bool:
    """Vrai si l'User-Agent trahit une sonde HTTP de type nmap (NSE)."""
    ua = user_agent.lower()
    return any(marker in ua for marker in _HTTP_SCANNER_MARKERS)


def scan_rule_name(scan_type: ScanType) -> str:
    return {
        ScanType.PORT_SCAN: "Nmap Port Scan Detected",
        ScanType.HTTP_PROBE: "Nmap HTTP Probe Detected",
        ScanType.VULN_SCAN: "Nmap Vulnerability Scan Detected",
    }[scan_type]


def scan_title(scan_type: ScanType, source_ip: str, port_count: int) -> str:
    if scan_type == ScanType.PORT_SCAN:
        return f"Scan de ports nmap depuis {source_ip} ({port_count} ports sondés)"
    if scan_type == ScanType.HTTP_PROBE:
        return f"Sondage HTTP de type nmap depuis {source_ip}"
    return f"Scan de vulnérabilités nmap depuis {source_ip}"
