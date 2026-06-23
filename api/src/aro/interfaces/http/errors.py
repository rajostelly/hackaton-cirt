from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from aro.domain.alerting.exceptions import AlertNotFound
from aro.domain.protection.exceptions import ProtectedIpError


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AlertNotFound)
    async def alert_not_found_handler(request: Request, exc: AlertNotFound) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ProtectedIpError)
    async def protected_ip_handler(request: Request, exc: ProtectedIpError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})
