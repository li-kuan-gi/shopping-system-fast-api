import os
import logging
import uuid
import time
from collections.abc import Callable, Awaitable
from fastapi import FastAPI, Request, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from contextvars import Token
from src.shopping.router import router as cart_router
from src.logging_config import setup_logging, log_context
from src.database import get_db

# Setup structured logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Shopping System API")


@app.middleware("http")
async def add_process_time_and_correlation_id(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    # Get correlation ID from header or generate a new one
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))

    # Set context for logging
    token: Token[dict[str, object]] = log_context.set(
        {
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
        }
    )

    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Correlation-ID"] = correlation_id

        # Log request completion
        logger.info(
            f"Request completed in {process_time:.4f}s with status {response.status_code}"
        )
        return response
    finally:
        log_context.reset(token)


# Security Middlewares
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
# Filter out empty strings if the env var is empty or only whitespace
allowed_origins = [o.strip() for o in allowed_origins if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

allowed_hosts = os.getenv("ALLOWED_HOSTS", "").split(",")
allowed_hosts = [h.strip() for h in allowed_hosts if h.strip()]

app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=allowed_hosts if allowed_hosts else ["*"]
)

# Render uses a proxy/load balancer
app.add_middleware(ProxyHeadersMiddleware)


@app.exception_handler(Exception)
async def global_exception_handler(_request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "An internal server error occurred."},
    )


@app.get("/")
async def root() -> dict[str, object]:
    return {
        "status": "success",
        "message": "Shopping System API is healthy",
        "environment": os.getenv("RENDER_EXTERNAL_URL", "development"),
    }


from typing import Annotated


@app.get("/health")
async def health(db: Annotated[Session, Depends(get_db)]) -> Response:
    """Robust health check that verifies database connectivity."""
    try:
        # Perform a simple query to verify DB connection
        _ = db.execute(text("SELECT 1"))
        return JSONResponse(content={"status": "ok", "database": "connected"})
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "database": "disconnected",
                "detail": "Internal health check failed",
            },
        )


app.include_router(cart_router)
