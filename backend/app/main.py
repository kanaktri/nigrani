import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1 import (alerts, analytics, assignments, attendance, auth,
                        cameras, evidence, grievances, institute_documents,
                        institutes, vc)
from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.base import Base, engine
from app.db.models import \
    *  # noqa: F401,F403 - ensures every model is registered on Base.metadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dosje_nigrani")

app = FastAPI(
    title=settings.APP_NAME,
    description="Smart Real-Time Monitoring & Inspection - SIH Problem Statement 26095",
    version="1.0.0",
)

# Dev convenience: for LOCAL SQLite development, tables are created
# directly from the models on startup, so `uvicorn app.main:app --reload`
# works immediately with no extra setup step. This is deliberately
# SQLite-only: mixing this with Alembic on a real database causes exactly
# the failure this comment used to hand-wave away as "a no-op" - if this
# ever runs even once against a fresh Postgres database before Alembic
# gets a chance to, Alembic's own migration then fails with
# "relation already exists", because the tables exist but Alembic's own
# version-tracking row was never written. Production (Postgres) must
# rely on `alembic upgrade head` alone, every time, with this skipped.
if settings.DATABASE_URL.startswith("sqlite"):
    Base.metadata.create_all(bind=engine)

# CORS_ORIGINS is read directly from settings, independent of DEBUG - the
# previous version tied this to DEBUG and ended up blocking every origin
# once DEBUG was turned off for production, which would have silently
# broken every frontend the moment this went live.
_origins = ["*"] if settings.CORS_ORIGINS == "*" else [o.strip() for o in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting: applied per-route (see auth.py's /login) rather than
# globally, so it protects the one endpoint worth protecting (password
# guessing) without throttling normal API use elsewhere.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Uniform 422 shape across the whole API instead of FastAPI's default verbose trace."""
    logger.warning("Validation error on %s: %s", request.url.path, exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation failed", "errors": exc.errors()},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.info("HTTP %s on %s: %s", exc.status_code, request.url.path, exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "service": settings.APP_NAME}


app.include_router(auth.router)
app.include_router(institutes.router)
app.include_router(assignments.router)
app.include_router(evidence.router)
app.include_router(alerts.router)
app.include_router(attendance.router)
app.include_router(vc.router)
app.include_router(grievances.router)
app.include_router(institute_documents.router)
app.include_router(cameras.router)
app.include_router(analytics.router)
