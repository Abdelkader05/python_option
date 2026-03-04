"""Point d'entree FastAPI du groupe 5."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.database import DatabaseError, init_database
from app.routers.votre_domaine import router as navigation_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_database()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API REST du groupe 5 pour les operateurs de navigation.",
    lifespan=lifespan,
)
app.include_router(navigation_router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = [
        {
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Les donnees fournies sont invalides",
            "details": errors,
            "path": str(request.url),
        },
    )


@app.exception_handler(DatabaseError)
async def database_exception_handler(
    request: Request, exc: DatabaseError
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "error": "database_error",
            "message": "Une erreur est survenue lors de l'acces aux donnees",
            "details": {"error": str(exc)},
            "path": str(request.url),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request, _: Exception
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "Une erreur interne est survenue",
            "path": str(request.url),
        },
    )


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Bienvenue sur l'API PlatonAAV Groupe 5",
        "documentation": "/docs",
        "version": settings.app_version,
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy", "database": "connected"}
