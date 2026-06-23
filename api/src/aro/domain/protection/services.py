from __future__ import annotations

from collections.abc import Iterable

# Adresses jamais bloquables (garde-fou de base, complété par PROTECTED_IPS).
_NEVER_BLOCK = frozenset({"127.0.0.1", "::1", "0.0.0.0"})


def is_protected_ip(ip: str, protected: Iterable[str]) -> bool:
    """Vrai si l'IP ne doit jamais être bloquée (loopback, admin, serveur…)."""
    return ip in _NEVER_BLOCK or ip in set(protected)
