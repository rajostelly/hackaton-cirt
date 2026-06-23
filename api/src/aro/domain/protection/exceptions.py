from __future__ import annotations


class ProtectedIpError(Exception):
    """Tentative de blocage d'une adresse protégée (SSH/admin/serveur)."""

    def __init__(self, ip: str) -> None:
        super().__init__(f"adresse protégée, blocage refusé: {ip}")
