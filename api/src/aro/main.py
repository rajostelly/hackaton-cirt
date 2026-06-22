from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aro.interfaces.http.errors import register_error_handlers
from aro.interfaces.http.routers.alerts import router as alerts_router
from aro.interfaces.http.routers.crowdstrike import router as crowdstrike_router
from aro.interfaces.http.routers.enrich import router as enrich_router
from aro.interfaces.http.routers.paloalto import router as paloalto_router
from aro.interfaces.http.routers.soc import router as soc_router
from aro.interfaces.http.routers.wazuh import router as wazuh_router
from aro.interfaces.http.schemas.alerts import HealthResponse

app = FastAPI(
    title="ARO API",
    description="Plateforme de supervision de sécurité pilotée par IA",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)
app.include_router(alerts_router)
app.include_router(enrich_router)
app.include_router(wazuh_router)
app.include_router(paloalto_router)
app.include_router(crowdstrike_router)
app.include_router(soc_router)


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")
