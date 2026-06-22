import asyncio
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
from aro.interfaces.http.routers.paloalto import router as paloalto_router
from aro.interfaces.http.routers.soc import router as soc_router
from aro.interfaces.http.routers.stream import router as stream_router
from aro.interfaces.http.routers.wazuh import router as wazuh_router
from aro.interfaces.http.schemas.alerts import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Lie le broker temps réel à la boucle asyncio courante pour permettre la
    # publication d'événements depuis les routes synchrones (threadpool).
    get_broker().bind_loop(asyncio.get_running_loop())
    # Initialise le repository (crée les tables si DATABASE_URL est défini).
    get_repository()
    yield


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
app.include_router(stream_router)
app.include_router(enrich_router)
app.include_router(wazuh_router)
app.include_router(paloalto_router)
app.include_router(crowdstrike_router)
app.include_router(soc_router)


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")
