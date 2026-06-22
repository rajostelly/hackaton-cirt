#!/usr/bin/env python3
"""Simule une détection de scan nmap (démo sans root/scapy).

Envoie une détection à l'API ARO exactement comme le ferait le capteur réseau,
ce qui déclenche une alerte temps réel sur le dashboard.

Exemples :
  python simulate_scan.py
  python simulate_scan.py --source-ip 203.0.113.66 --ports 80 ports=200
  ARO_API_URL=http://localhost:8000 python simulate_scan.py --type vuln_scan
"""
from __future__ import annotations

import argparse
import os
import random

import requests

ARO_API_URL = os.environ.get("ARO_API_URL", "http://localhost:8000").rstrip("/")
TARGET = os.environ.get("SENSOR_TARGET", "sfyrisec.duckdns.org")


def main() -> None:
    parser = argparse.ArgumentParser(description="Simule un scan nmap vers ARO")
    parser.add_argument("--source-ip", default=f"203.0.113.{random.randint(2, 250)}")
    parser.add_argument(
        "--type",
        dest="scan_type",
        default="port_scan",
        choices=["port_scan", "http_probe", "vuln_scan"],
    )
    parser.add_argument("--ports", type=int, default=42, help="nombre de ports sondés")
    args = parser.parse_args()

    ports = sorted(random.sample(range(1, 1025), min(args.ports, 1024)))
    payload = {
        "source_ip": args.source_ip,
        "scan_type": args.scan_type,
        "ports": ports,
        "target": TARGET,
        "packet_count": len(ports),
        "detail": "Détection simulée (démo)",
    }
    resp = requests.post(f"{ARO_API_URL}/detections/scan", json=payload, timeout=5)
    resp.raise_for_status()
    data = resp.json()
    print(f"Alerte créée: {data['id']} · {data['criticity']} · {data['title']}")


if __name__ == "__main__":
    main()
