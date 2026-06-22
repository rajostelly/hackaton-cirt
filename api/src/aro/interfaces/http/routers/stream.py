from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from aro.infrastructure.realtime.broker import AlertBroker
from aro.interfaces.http.dependencies import get_broker

router = APIRouter(prefix="/stream", tags=["stream"])

# Intervalle d'envoi d'un commentaire de maintien de connexion (anti-timeout proxy).
HEARTBEAT_SECONDS = 15.0


async def event_stream(broker: AlertBroker, request: Request) -> AsyncIterator[str]:
    queue = await broker.subscribe()
    try:
        yield ": connected\n\n"
        while True:
            if await request.is_disconnected():
                break
            try:
                payload = await asyncio.wait_for(queue.get(), timeout=HEARTBEAT_SECONDS)
                yield f"data: {payload}\n\n"
            except TimeoutError:
                yield ": keep-alive\n\n"
    finally:
        broker.unsubscribe(queue)


@router.get("/alerts")
async def stream_alerts(
    request: Request,
    broker: AlertBroker = Depends(get_broker),
) -> StreamingResponse:
    """Flux SSE : chaque alerte créée/mise à jour est poussée au dashboard."""
    return StreamingResponse(
        event_stream(broker, request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
