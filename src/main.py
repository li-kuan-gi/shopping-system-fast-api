import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from fastapi.responses import JSONResponse

from src.routers import cart
from src.logging_config import setup_logging

# Setup structured logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Shopping System API")

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
    TrustedHostMiddleware, 
    allowed_hosts=allowed_hosts if allowed_hosts else ["*"]
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
async def root():
    return {
        "status": "success", 
        "message": "Shopping System API is healthy",
        "environment": os.getenv("RENDER_EXTERNAL_URL", "development")
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(cart.router)
