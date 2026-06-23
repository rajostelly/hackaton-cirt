import asyncio
import contextlib
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool

try:
    from dotenv import load_dotenv

    load_dotenv()  # charge api/.env si présent (DATABASE_URL, clés, etc.)
except ImportError:  # python-dotenv optionnel
    pass

from aro.interfaces.http.dependencies import get_broker, get_repository
from aro.interfaces.http.errors import register_error_handlers
from aro.interfaces.http.middleware import NmapHttpProbeMiddleware
from aro.interfaces.http.routers.alerts import router as alerts_router
from aro.interfaces.http.routers.crowdstrike import router as crowdstrike_router
from aro.interfaces.http.routers.detections import router as detections_router
from aro.interfaces.http.routers.enrich import router as enrich_router
from aro.interfaces.http.routers.incidents import router as incidents_router
from aro.interfaces.http.routers.ml import router as ml_router
from aro.interfaces.http.routers.paloalto import router as paloalto_router
from aro.interfaces.http.routers.protection import router as protection_router
from aro.interfaces.http.routers.soc import router as soc_router
from aro.interfaces.http.routers.stream import router as stream_router
from aro.interfaces.http.routers.virus import router as virus_router
from aro.interfaces.http.routers.vulnerabilities import router as vulnerabilities_router
from aro.interfaces.http.routers.wazuh import router as wazuh_router
from aro.interfaces.http.schemas.alerts import HealthResponse


async def _incident_loop() -> None:
    # Analyse périodique du réseau (tshark) pour alimenter les incidents en continu.
    from aro.interfaces.http.dependencies import get_analyze_incidents_use_case

    interval = int(os.environ.get("INCIDENTS_INTERVAL", "20"))
    while True:
        await asyncio.sleep(interval)
        with contextlib.suppress(Exception):
            await run_in_threadpool(get_analyze_incidents_use_case().execute)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Lie le broker temps réel à la boucle asyncio courante pour permettre la
    # publication d'événements depuis les routes synchrones (threadpool).
    get_broker().bind_loop(asyncio.get_running_loop())
    # Initialise le repository (crée les tables si DATABASE_URL est défini).
    get_repository()
    task: asyncio.Task | None = None
    if os.environ.get("INCIDENTS_LIVE") == "true":
        task = asyncio.create_task(_incident_loop())
    try:
        yield
    finally:
        if task is not None:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task


app = FastAPI(
    title="ARO API",
    description="Plateforme de supervision de sécurité pilotée par IA",
    version="0.1.0",
    lifespan=lifespan,
)

# Origines autorisées configurables (front local + serveur). CORS_ORIGINS =
# liste séparée par des virgules.
_default_origins = "http://localhost:5173,http://localhost:4173"
_cors_origins = [
    o.strip()
    for o in os.environ.get("CORS_ORIGINS", _default_origins).split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Détection des sondes HTTP nmap (User-Agent NSE) sur toutes les requêtes.
app.add_middleware(NmapHttpProbeMiddleware)

register_error_handlers(app)
app.include_router(alerts_router)
app.include_router(detections_router)
app.include_router(protection_router)
app.include_router(vulnerabilities_router)
app.include_router(ml_router)
app.include_router(incidents_router)
app.include_router(virus_router)
app.include_router(stream_router)
app.include_router(enrich_router)
app.include_router(wazuh_router)
app.include_router(paloalto_router)
app.include_router(crowdstrike_router)
app.include_router(soc_router)


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")
