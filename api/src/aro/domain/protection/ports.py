from __future__ import annotations

from typing import Protocol


class FirewallBlocker(Protocol):
    """Port de blocage réseau (implémenté par nftables ou en mémoire)."""

    def block(self, ip: str) -> None: ...
    def unblock(self, ip: str) -> None: ...
    def list_blocked(self) -> list[str]: ...
