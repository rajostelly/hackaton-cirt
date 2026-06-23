from __future__ import annotations

import contextlib
import subprocess
from collections.abc import Callable
from typing import Any

# runner(iface, duration) -> CSV "ip.src,ip.dst,frame.len". Injectable (tests).
Runner = Callable[..., str]


def _default_runner(iface: str, duration: int) -> str:
    result = subprocess.run(
        [
            "tshark", "-i", iface, "-a", f"duration:{duration}", "-n", "-q",
            "-T", "fields", "-e", "ip.src", "-e", "ip.dst", "-e", "frame.len",
            "-E", "separator=,",
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=duration + 30,
    )
    return result.stdout


def parse_incident_flows(output: str) -> tuple[list[dict[str, Any]], int]:
    """Agrège les paquets en flux par source (avec IP destinations) + total."""
    agg: dict[str, dict[str, Any]] = {}
    total = 0
    for line in output.splitlines():
        parts = line.split(",")
        if len(parts) < 3 or not parts[0]:
            continue
        src, dst, length = parts[0], parts[1], parts[2]
        total += 1
        flow = agg.setdefault(src, {"source_ip": src, "_dsts": set(), "packets": 0, "bytes": 0})
        flow["packets"] += 1
        if dst:
            flow["_dsts"].add(dst)
        with contextlib.suppress(ValueError):
            flow["bytes"] += int(length)

    flows = [
        {
            "source_ip": f["source_ip"],
            "dst_ips": sorted(f["_dsts"]),
            "packets": f["packets"],
            "bytes": f["bytes"],
        }
        for f in agg.values()
    ]
    return flows, total


class TsharkIncidentCollector:
    def __init__(self, runner: Runner = _default_runner, iface: str = "eth0", duration: int = 8):
        self._runner = runner
        self._iface = iface
        self._duration = duration

    def capture(self) -> tuple[list[dict[str, Any]], int]:
        try:
            output = self._runner(self._iface, self._duration)
        except Exception:  # noqa: BLE001 - capture best-effort
            return [], 0
        return parse_incident_flows(output)
