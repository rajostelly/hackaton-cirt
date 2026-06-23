from __future__ import annotations

from dataclasses import dataclass

from aro.domain.protection.value_objects import ProtectionMode


@dataclass
class ProtectionSettings:
    """État runtime du mode de protection (modifiable via l'API)."""

    mode: ProtectionMode = ProtectionMode.IDS
