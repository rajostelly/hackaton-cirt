from __future__ import annotations

from pydantic import BaseModel

from aro.domain.protection.value_objects import ProtectionMode


class ModeIn(BaseModel):
    mode: ProtectionMode


class ModeOut(BaseModel):
    mode: ProtectionMode


class BlockIn(BaseModel):
    source_ip: str


class BlockedOut(BaseModel):
    blocked: list[str]
