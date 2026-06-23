from __future__ import annotations


class InMemoryBlocker:
    """Bloqueur en mémoire (dev/tests, pas d'effet réseau réel)."""

    def __init__(self) -> None:
        self._blocked: set[str] = set()

    def block(self, ip: str) -> None:
        self._blocked.add(ip)

    def unblock(self, ip: str) -> None:
        self._blocked.discard(ip)

    def list_blocked(self) -> list[str]:
        return sorted(self._blocked)
