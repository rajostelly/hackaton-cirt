from __future__ import annotations

import contextlib
import subprocess
from collections.abc import Callable

# runner(iface, duration) -> sortie CSV de tshark. Injectable (tests).
Runner = Callable[..., str]


def _default_runner(iface: str, duration: int) -> str:
    result = subprocess.run(
        [
            "tshark", "-i", iface, "-a", f"duration:{duration}", "-n", "-q",
            "-T", "fields",
            "-e", "ip.src", "-e", "ip.dst", "-e", "tcp.dstport",
            "-e", "frame.len", "-e", "tcp.flags.syn",
            "-E", "separator=,",
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=duration + 30,
    )
    return result.stdout


def parse_flows(output: str) -> list[dict]:
    """Agrège les paquets capturés en flux par IP source (features réseau)."""
    agg: dict[str, dict] = {}
    for line in output.splitlines():
        parts = line.split(",")
        if len(parts) < 5 or not parts[0]:
            continue
        src, dst, dport, length, syn = parts[0], parts[1], parts[2], parts[3], parts[4]
        flow = agg.setdefault(
            src,
            {"source_ip": src, "packets": 0, "_ports": set(), "_ips": set(), "bytes": 0,
             "syn_count": 0},
        )
        flow["packets"] += 1
        if dport:
            flow["_ports"].add(dport)
        if dst:
            flow["_ips"].add(dst)
        with contextlib.suppress(ValueError):
            flow["bytes"] += int(length)
        if syn == "1":
            flow["syn_count"] += 1

    return [
        {
            "source_ip": f["source_ip"],
            "packets": f["packets"],
            "distinct_dst_ports": len(f["_ports"]),
            "distinct_dst_ips": len(f["_ips"]),
            "bytes": f["bytes"],
            "syn_count": f["syn_count"],
        }
        for f in agg.values()
    ]


class TsharkCollector:
    def __init__(self, runner: Runner = _default_runner, iface: str = "eth0", duration: int = 10):
        self._runner = runner
        self._iface = iface
        self._duration = duration

    def capture(self) -> list[dict]:
        try:
            output = self._runner(self._iface, self._duration)
        except Exception:  # noqa: BLE001 - capture best-effort
            return []
        return parse_flows(output)
