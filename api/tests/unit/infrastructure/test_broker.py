import asyncio

from aro.infrastructure.realtime.broker import AlertBroker


def test_publish_delivers_to_subscriber() -> None:
    async def scenario() -> str:
        broker = AlertBroker()
        broker.bind_loop(asyncio.get_running_loop())
        queue = await broker.subscribe()
        broker.publish("alert.created", {"id": "abc"})
        await asyncio.sleep(0.01)  # laisse call_soon_threadsafe s'exécuter
        return await asyncio.wait_for(queue.get(), timeout=1)

    msg = asyncio.run(scenario())
    assert '"type": "alert.created"' in msg
    assert '"id": "abc"' in msg


def test_publish_without_loop_is_synchronous() -> None:
    async def scenario() -> str:
        broker = AlertBroker()  # pas de bind_loop -> envoi direct
        queue = await broker.subscribe()
        broker.publish("e", {"a": 1})
        return queue.get_nowait()

    msg = asyncio.run(scenario())
    assert '"a": 1' in msg


def test_subscribe_unsubscribe_counts() -> None:
    async def scenario() -> tuple[int, int]:
        broker = AlertBroker()
        queue = await broker.subscribe()
        after_sub = broker.subscriber_count
        broker.unsubscribe(queue)
        return after_sub, broker.subscriber_count

    after_sub, after_unsub = asyncio.run(scenario())
    assert after_sub == 1
    assert after_unsub == 0


def test_publish_when_queue_full_is_dropped() -> None:
    async def scenario() -> int:
        broker = AlertBroker(max_queue=1)
        queue = await broker.subscribe()
        broker.publish("e", {"n": 1})
        broker.publish("e", {"n": 2})  # file pleine -> ignoré sans erreur
        return queue.qsize()

    assert asyncio.run(scenario()) == 1
