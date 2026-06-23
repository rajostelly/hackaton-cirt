from __future__ import annotations

import time
from collections.abc import Awaitable, Callable

from starlette.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from aro.application.detection.dto import ScanDetectionInput
from aro.application.detection.use_cases import RecordScanDetectionUseCase
from aro.domain.detection.services import is_nmap_http_probe
from aro.domain.detection.value_objects import ScanType
from aro.interfaces.http import mappers
from aro.interfaces.http.dependencies import (
    auto_block,
    get_broker,
    get_explainer,
    get_repository,
)
from aro.interfaces.http.routers.detections import enrich_with_ai


def client_ip(request: Request) -> str:
    """IP source réelle : derrière nginx, prend le 1er X-Forwarded-For."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "0.0.0.0"


class NmapHttpProbeMiddleware(BaseHTTPMiddleware):
    """Détecte les sondes HTTP de type nmap (User-Agent NSE) et lève une alerte.

    Complète le capteur réseau : ici on attrape les scans applicatifs (`nmap
    -sV --script http-*`) qui traversent le reverse-proxy. Anti-spam par IP.
    """

    def __init__(self, app: object, cooldown_seconds: float = 60.0) -> None:
        super().__init__(app)  # type: ignore[arg-type]
        self._cooldown = cooldown_seconds
        self._last_seen: dict[str, float] = {}

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        user_agent = request.headers.get("user-agent", "")
        if is_nmap_http_probe(user_agent):
            source = client_ip(request)
            if self._cooldown_ok(source):
                # En threadpool : l'écriture DB / l'appel IA ne bloque pas la boucle.
                await run_in_threadpool(self._record, source, request.url.path, user_agent)
        return await call_next(request)

    def _cooldown_ok(self, source: str) -> bool:
        now = time.time()
        if now - self._last_seen.get(source, 0.0) < self._cooldown:
            return False
        self._last_seen[source] = now
        return True

    def _record(self, source: str, path: str, user_agent: str) -> None:
        repo = get_repository()
        broker = get_broker()
        try:
            result = RecordScanDetectionUseCase(repository=repo).execute(
                ScanDetectionInput(
                    source_ip=source,
                    scan_type=ScanType.HTTP_PROBE,
                    ports=[],
                    detail=f"Sonde HTTP nmap sur {path} (UA: {user_agent[:120]})",
                )
            )
        except ValueError:
            return  # IP non IPv4 (ex. IPv6 / hôte inconnu) — on ignore
        broker.publish("alert.created", mappers.to_alert_out(result).model_dump(mode="json"))
        auto_block(result.source_ip)  # blocage pare-feu automatique si mode IPS
        enrich_with_ai(result.id, repo, get_explainer(), broker)
