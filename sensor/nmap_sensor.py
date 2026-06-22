#!/usr/bin/env python3
"""Capteur de scan de ports (type nmap) pour ARO.

Sniffe le trafic TCP entrant et détecte un balayage de ports : une même IP
source qui touche un grand nombre de ports distincts dans une courte fenêtre.
Chaque détection est envoyée à l'API ARO (`POST /detections/scan`), qui crée
une alerte et la pousse en temps réel sur le dashboard (SSE).

À lancer sur le serveur exposé par `sfyrisec.duckdns.org` (accès root/raw socket
requis pour la capture). En l'absence de scapy ou de privilèges, utilisez plutôt
`simulate_scan.py` pour démontrer le pipeline temps réel.

Variables d'environnement :
  ARO_API_URL        URL de base de l'API ARO        (def. http://localhost:8000)
  SENSOR_TARGET      étiquette de la cible surveillée (def. sfyrisec.duckdns.org)
  SENSOR_IFACE       interface réseau à écouter       (def. toutes)
  SCAN_PORT_THRESHOLD nb de ports distincts déclencheur (def. 10)
  SCAN_WINDOW_SECONDS fenêtre glissante en secondes    (def. 10)
  SCAN_COOLDOWN_SECONDS anti-spam par IP source         (def. 60)
"""
from __future__ import annotations

import os
import sys
import time
from collections import defaultdict

import requests

try:
    from scapy.all import IP, TCP, sniff  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover - dépend de l'environnement d'exécution
    print(
        "scapy n'est pas installé. Installez-le (`pip install scapy`) et lancez "
        "ce capteur en root, ou utilisez simulate_scan.py pour la démo.",
        file=sys.stderr,
    )
    raise SystemExit(1) from None

ARO_API_URL = os.environ.get("ARO_API_URL", "http://localhost:8000").rstrip("/")
TARGET = os.environ.get("SENSOR_TARGET", "sfyrisec.duckdns.org")
IFACE = os.environ.get("SENSOR_IFACE") or None
PORT_THRESHOLD = int(os.environ.get("SCAN_PORT_THRESHOLD", "10"))
WINDOW = float(os.environ.get("SCAN_WINDOW_SECONDS", "10"))
COOLDOWN = float(os.environ.get("SCAN_COOLDOWN_SECONDS", "60"))

# Drapeaux TCP : on ne garde que les SYN « purs » (début de connexion / scan),
# pas les SYN-ACK (réponses légitimes du serveur).
_SYN = 0x02
_ACK = 0x10

# Par IP source : {port: timestamp} des SYN récents.
_seen: dict[str, dict[int, float]] = defaultdict(dict)
# Par IP source : dernier envoi d'alerte (anti-spam).
_last_alert: dict[str, float] = {}


def _report(source_ip: str, ports: list[int]) -> None:
    payload = {
        "source_ip": source_ip,
        "scan_type": "port_scan",
        "ports": ports,
        "target": TARGET,
        "packet_count": len(ports),
        "detail": f"{len(ports)} ports distincts sondés en < {WINDOW:.0f}s",
    }
    try:
        resp = requests.post(f"{ARO_API_URL}/detections/scan", json=payload, timeout=5)
        resp.raise_for_status()
        print(f"[ALERTE] scan de {source_ip} ({len(ports)} ports) -> ARO #{resp.json().get('id')}")
    except requests.RequestException as exc:
        print(f"[ERREUR] envoi à l'API échoué: {exc}", file=sys.stderr)


def _handle(packet: object) -> None:
    if not packet.haslayer(TCP) or not packet.haslayer(IP):  # type: ignore[attr-defined]
        return
    flags = int(packet[TCP].flags)  # type: ignore[index]
    if not (flags & _SYN) or (flags & _ACK):
        return  # pas un SYN pur

    now = time.time()
    src = packet[IP].src  # type: ignore[index]
    dport = int(packet[TCP].dport)  # type: ignore[index]

    ports = _seen[src]
    ports[dport] = now
    # Purge des ports hors de la fenêtre glissante.
    for p, ts in list(ports.items()):
        if now - ts > WINDOW:
            del ports[p]

    if len(ports) >= PORT_THRESHOLD and now - _last_alert.get(src, 0) > COOLDOWN:
        _last_alert[src] = now
        _report(src, sorted(ports.keys()))


def main() -> None:
    print(
        f"Capteur ARO démarré · cible={TARGET} · seuil={PORT_THRESHOLD} ports/"
        f"{WINDOW:.0f}s · API={ARO_API_URL}"
    )
    sniff(filter="tcp", prn=_handle, store=False, iface=IFACE)


if __name__ == "__main__":
    main()
