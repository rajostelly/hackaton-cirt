import asyncio

from aro.infrastructure.realtime.broker import AlertBroker
from aro.interfaces.http.routers import stream


class _FakeRequest:
    """Faux Request : se déconnecte après `disconnect_after` vérifications."""

    def __init__(self, disconnect_after: int) -> None:
        self._calls = 0
        self._disconnect_after = disconnect_after

    async def is_disconnected(self) -> bool:
        self._calls += 1
        return self._calls > self._disconnect_after


def test_event_stream_emits_connected_then_event() -> None:
    async def scenario() -> tuple[str, str, bool]:
        broker = AlertBroker()
        broker.bind_loop(asyncio.get_running_loop())
        req = _FakeRequest(disconnect_after=1)
        gen = stream.event_stream(broker, req)  # type: ignore[arg-type]

        connected = await gen.__anext__()
        broker.publish("alert.created", {"id": "abc"})
        await asyncio.sleep(0.01)
        event = await gen.__anext__()

        stopped = False
        try:
            await gen.__anext__()
        except StopAsyncIteration:
            stopped = True
        return connected, event, stopped

    connected, event, stopped = asyncio.run(scenario())
    assert connected.startswith(": connected")
    assert "alert.created" in event
    assert event.startswith("data: ")
    assert stopped is True


def test_event_stream_sends_keepalive_on_idle(monkeypatch) -> None:
    monkeypatch.setattr(stream, "HEARTBEAT_SECONDS", 0.01)

    async def scenario() -> str:
        broker = AlertBroker()
        broker.bind_loop(asyncio.get_running_loop())
        req = _FakeRequest(disconnect_after=2)
        gen = stream.event_stream(broker, req)  # type: ignore[arg-type]
        await gen.__anext__()  # ": connected"
        return await gen.__anext__()  # timeout -> keep-alive

    keepalive = asyncio.run(scenario())
    assert "keep-alive" in keepalive
