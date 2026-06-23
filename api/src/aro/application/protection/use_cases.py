from __future__ import annotations

from dataclasses import dataclass

from aro.domain.protection.exceptions import ProtectedIpError
from aro.domain.protection.ports import FirewallBlocker
from aro.domain.protection.services import is_protected_ip
from aro.domain.protection.value_objects import ProtectionMode
from aro.domain.shared.value_objects import IpAddress


@dataclass
class BlockIpUseCase:
    blocker: FirewallBlocker
    protected_ips: frozenset[str]

    def execute(self, ip: str) -> None:
        IpAddress(ip)  # valide le format (lève ValueError sinon)
        if is_protected_ip(ip, self.protected_ips):
            raise ProtectedIpError(ip)
        self.blocker.block(ip)


@dataclass
class UnblockIpUseCase:
    blocker: FirewallBlocker

    def execute(self, ip: str) -> None:
        IpAddress(ip)
        self.blocker.unblock(ip)


@dataclass
class ListBlockedUseCase:
    blocker: FirewallBlocker

    def execute(self) -> list[str]:
        return self.blocker.list_blocked()


@dataclass
class AutoBlockUseCase:
    """Blocage automatique en mode IPS (utilisé par la chaîne de détection)."""

    blocker: FirewallBlocker
    protected_ips: frozenset[str]

    def execute(self, ip: str, mode: ProtectionMode) -> bool:
        if mode != ProtectionMode.IPS:
            return False
        if is_protected_ip(ip, self.protected_ips):
            return False
        try:
            self.blocker.block(ip)
            return True
        except Exception:  # noqa: BLE001 - le blocage ne doit jamais casser l'ingestion
            return False
