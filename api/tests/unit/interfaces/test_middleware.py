from starlette.requests import Request

from aro.domain.shared.value_objects import Criticity
from aro.infrastructure.alerting.memory_repo import InMemoryAlertRepository
from aro.infrastructure.realtime.broker import AlertBroker
from aro.interfaces.http import middleware
from aro.interfaces.http.middleware import NmapHttpProbeMiddleware, client_ip


def _request(headers: list[tuple[bytes, bytes]], client: tuple[str, int] | None) -> Request:
    scope: dict = {"type": "http", "headers": headers}
    if client is not None:
        scope["client"] = client
    return Request(scope)


def test_client_ip_prefers_forwarded_for() -> None:
    req = _request([(b"x-forwarded-for", b"203.0.113.9, 10.0.0.1")], ("10.0.0.1", 1234))
    assert client_ip(req) == "203.0.113.9"


def test_client_ip_falls_back_to_peer() -> None:
    assert client_ip(_request([], ("198.51.100.5", 1234))) == "198.51.100.5"


def test_client_ip_without_client_is_placeholder() -> None:
    assert client_ip(_request([], None)) == "0.0.0.0"


def _middleware() -> NmapHttpProbeMiddleware:
    async def _app(scope, receive, send):  # pragma: no cover - jamais appelé ici
        return None

    return NmapHttpProbeMiddleware(_app)


def test_cooldown_blocks_repeat_within_window() -> None:
    mw = _middleware()
    assert mw._cooldown_ok("203.0.113.1") is True
    assert mw._cooldown_ok("203.0.113.1") is False  # 2e dans la fenêtre
    assert mw._cooldown_ok("203.0.113.2") is True  # autre IP


def test_record_creates_http_probe_alert(monkeypatch) -> None:
    repo = InMemoryAlertRepository()
    broker = AlertBroker()
    monkeypatch.setattr(middleware, "get_repository", lambda: repo)
    monkeypatch.setattr(middleware, "get_broker", lambda: broker)

    mw = _middleware()
    mw._record("203.0.113.50", "/wp-login.php", "Nmap Scripting Engine")

    alerts = repo.list_open(limit=10, criticity=None)
    assert len(alerts) == 1
    assert alerts[0].criticity == Criticity.HIGH
    assert "HTTP" in alerts[0].rule_name
    assert alerts[0].explanation  # explication de repli attachée


def test_record_ignores_non_ipv4_source(monkeypatch) -> None:
    repo = InMemoryAlertRepository()
    monkeypatch.setattr(middleware, "get_repository", lambda: repo)
    monkeypatch.setattr(middleware, "get_broker", lambda: AlertBroker())

    mw = _middleware()
    mw._record("::1", "/", "nmap")  # IPv6 -> ignoré sans erreur

    assert repo.list_open(limit=10, criticity=None) == []
