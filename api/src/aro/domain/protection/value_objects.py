from __future__ import annotations

from enum import StrEnum


class ProtectionMode(StrEnum):
    """Mode de protection du SOC.

    IDS : on détecte et on alerte uniquement (aucun blocage).
    IPS : on détecte ET on bloque automatiquement l'attaquant au pare-feu.
    """

    IDS = "ids"
    IPS = "ips"
