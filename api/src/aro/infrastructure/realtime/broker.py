from __future__ import annotations

import asyncio
import contextlib
import json
from typing import Any


class AlertBroker:
    """Pub/sub asynchrone en mémoire pour pousser les événements d'alerte (SSE).

    `publish` est appelable depuis un contexte synchrone (les routes FastAPI
    sync tournent dans un threadpool) : on planifie l'envoi sur la boucle
    asyncio via `call_soon_threadsafe`. La boucle est liée au démarrage de
    l'app (`bind_loop`).
    """

    def __init__(self, max_queue: int = 100) -> None:
        self._subscribers: set[asyncio.Queue[str]] = set()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._max_queue = max_queue

    def bind_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    @property
    def subscriber_count(self) -> int:
        return len(self._subscribers)

    async def subscribe(self) -> asyncio.Queue[str]:
        queue: asyncio.Queue[str] = asyncio.Queue(maxsize=self._max_queue)
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[str]) -> None:
        self._subscribers.discard(queue)

    def publish(self, event_type: str, data: dict[str, Any]) -> None:
        payload = json.dumps({"type": event_type, "data": data}, default=str)
        loop = self._loop
        for queue in list(self._subscribers):
            if loop is not None and loop.is_running():
                loop.call_soon_threadsafe(self._safe_put, queue, payload)
            else:
                self._safe_put(queue, payload)

    @staticmethod
    def _safe_put(queue: asyncio.Queue[str], payload: str) -> None:
        # Abonné lent (file pleine) : on saute l'événement plutôt que de bloquer.
        with contextlib.suppress(asyncio.QueueFull):
            queue.put_nowait(payload)
