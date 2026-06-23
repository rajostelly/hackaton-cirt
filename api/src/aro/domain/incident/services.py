from __future__ import annotations

from typing import Any


def ip_segment(ip: str) -> str | None:
    """Segment réseau interne (RFC1918) d'une IP, sinon None.

    192.168.x.y -> "192.168.x" (/24) ; 10.x -> "10.x" ; 172.16-31 -> "172.x".
    """
    parts = ip.split(".")
    if len(parts) != 4 or not all(p.isdigit() for p in parts):
        return None
    a, b = int(parts[0]), int(parts[1])
    if a == 10:
        return f"10.{b}"
    if a == 192 and b == 168:
        return f"192.168.{parts[2]}"
    if a == 172 and 16 <= b <= 31:
        return f"172.{b}"
    return None


def detect_traffic_spike(total_packets: int, threshold: int) -> bool:
    return total_packets >= threshold


def detect_lateral_movement(flows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Repère une source interne qui contacte un AUTRE segment interne.

    Ex. concret : une machine du réseau RH (192.168.10.x) qui ouvre des
    connexions vers le réseau Finance (192.168.20.x) — déplacement latéral.
    """
    findings: list[dict[str, Any]] = []
    for flow in flows:
        source = flow.get("source_ip", "")
        src_seg = ip_segment(source)
        if src_seg is None:
            continue
        other_segments = sorted(
            {
                seg
                for dst in flow.get("dst_ips", [])
                if (seg := ip_segment(dst)) is not None and seg != src_seg
            }
        )
        if other_segments:
            findings.append(
                {
                    "source_ip": source,
                    "src_segment": src_seg,
                    "target_segments": other_segments,
                }
            )
    return findings
