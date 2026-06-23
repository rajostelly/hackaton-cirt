from __future__ import annotations

import contextlib
import re
import subprocess
from collections.abc import Callable

# runner(args, stdin) -> stdout. Injectable pour les tests.
Runner = Callable[..., str]

_FAMILY = "inet"
_TABLE = "aro_ips"
_SET = "blocked"

# Garde-fou : SSH (port 22) est TOUJOURS accepté avant la règle de drop,
# donc un IP bloqué ne peut jamais couper l'administration de la machine.
_RULESET = """
table inet aro_ips {
  set blocked { type ipv4_addr; }
  chain input {
    type filter hook input priority -150; policy accept;
    tcp dport 22 accept;
    ip saddr @blocked drop;
  }
}
"""


def _default_runner(args: list[str], stdin: str | None = None) -> str:
    result = subprocess.run(
        ["nft", *args], check=True, capture_output=True, text=True, input=stdin
    )
    return result.stdout


class NftBlocker:
    """Bloqueur IPS via nftables (set `inet aro_ips blocked`).

    La table est créée à l'initialisation si absente, sans écraser les blocages
    existants (idempotent au redémarrage).
    """

    def __init__(self, runner: Runner = _default_runner) -> None:
        self._run = runner
        self._ensure_table()

    def _ensure_table(self) -> None:
        try:
            self._run(["list", "table", _FAMILY, _TABLE])
        except Exception:
            self._run(["-f", "-"], stdin=_RULESET)

    def block(self, ip: str) -> None:
        with contextlib.suppress(Exception):  # déjà bloqué -> ignore
            self._run(["add", "element", _FAMILY, _TABLE, _SET, f"{{ {ip} }}"])

    def unblock(self, ip: str) -> None:
        with contextlib.suppress(Exception):  # absent -> ignore
            self._run(["delete", "element", _FAMILY, _TABLE, _SET, f"{{ {ip} }}"])

    def list_blocked(self) -> list[str]:
        try:
            out = self._run(["list", "set", _FAMILY, _TABLE, _SET])
        except Exception:
            return []
        match = re.search(r"elements\s*=\s*\{([^}]*)\}", out)
        if not match:
            return []
        return sorted(x.strip() for x in match.group(1).split(",") if x.strip())
