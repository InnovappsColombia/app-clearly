"""
CLEARLY — Main FastAPI Application Entrypoint
Sovereign Civic Accessibility & Community Ecosystem Backend.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.api.v1.router import api_router
from app.core.config import settings
from app.services.legal_guardrail import LegalGuardrailViolation


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event handler for startup and graceful shutdown."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} ({settings.ENVIRONMENT})")
    logger.info(f"FastAPI Docs available at: {settings.API_V1_STR}/docs")
    yield
    logger.info(f"Shutting down {settings.APP_NAME}...")


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "**CLEARLY — Tu comunidad. Más clara.** *(Your community. Made clear.)*\n\n"
        "Ecosistema omnicanal de inclusión ciudadana, accesibilidad gerontológica y soberanía de datos.\n"
        "Sprint 1: Backend Core, Ingesta Documental, Extracción Temporal Determinista y Lenguaje Claro (FH >= 80)."
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler for Legal Guardrail violations
@app.exception_handler(LegalGuardrailViolation)
async def legal_guardrail_exception_handler(request: Request, exc: LegalGuardrailViolation):
    logger.warning(f"Legal Guardrail Blocked Request: {exc.matched_text}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "LEGAL_GUARDRAIL_VIOLATION",
            "message": str(exc),
            "matched_expression": exc.matched_text,
            "escalation_recommendation": (
                "Este caso requiere evaluación por un profesional certificado. "
                "Utilice CLEARLY Premium para agendar una consulta con un experto verificado."
            ),
        },
    )


# Exception handler for general ValueErrors
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "VALIDATION_ERROR", "detail": str(exc)},
    )


# Mount API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
async def root():
    """Root landing endpoint with system status and links."""
    return {
        "app": settings.APP_NAME,
        "tagline": "Tu comunidad. Más clara. (Your community. Made clear.)",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "online",
        "api_v1_docs": f"{settings.API_V1_STR}/docs",
        "health_endpoint": f"{settings.API_V1_STR}/health",
    }

