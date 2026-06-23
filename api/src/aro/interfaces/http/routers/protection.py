from __future__ import annotations

from fastapi import APIRouter, Depends

from aro.application.protection.use_cases import (
    BlockIpUseCase,
    ListBlockedUseCase,
    UnblockIpUseCase,
)
from aro.infrastructure.protection.settings import ProtectionSettings
from aro.interfaces.http.dependencies import (
    get_block_use_case,
    get_list_blocked_use_case,
    get_protection_settings,
    get_unblock_use_case,
)
from aro.interfaces.http.schemas.protection import BlockedOut, BlockIn, ModeIn, ModeOut

router = APIRouter(prefix="/protection", tags=["protection"])


@router.get("/mode", response_model=ModeOut)
def get_mode(settings: ProtectionSettings = Depends(get_protection_settings)) -> ModeOut:
    return ModeOut(mode=settings.mode)


@router.put("/mode", response_model=ModeOut)
def set_mode(
    payload: ModeIn,
    settings: ProtectionSettings = Depends(get_protection_settings),
) -> ModeOut:
    settings.mode = payload.mode
    return ModeOut(mode=settings.mode)


@router.get("/blocked", response_model=BlockedOut)
def list_blocked(
    use_case: ListBlockedUseCase = Depends(get_list_blocked_use_case),
) -> BlockedOut:
    return BlockedOut(blocked=use_case.execute())


@router.post("/block", response_model=BlockedOut, status_code=201)
def block_ip(
    payload: BlockIn,
    use_case: BlockIpUseCase = Depends(get_block_use_case),
    lister: ListBlockedUseCase = Depends(get_list_blocked_use_case),
) -> BlockedOut:
    use_case.execute(payload.source_ip)
    return BlockedOut(blocked=lister.execute())


@router.post("/unblock", response_model=BlockedOut)
def unblock_ip(
    payload: BlockIn,
    use_case: UnblockIpUseCase = Depends(get_unblock_use_case),
    lister: ListBlockedUseCase = Depends(get_list_blocked_use_case),
) -> BlockedOut:
    use_case.execute(payload.source_ip)
    return BlockedOut(blocked=lister.execute())
