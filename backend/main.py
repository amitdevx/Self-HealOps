import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from backend.core.logging import setup_logging

def create_app() -> FastAPI:
    # Setup structured logging
    setup_logging(settings.ENVIRONMENT)
    logger = logging.getLogger(__name__)
    logger.info(f"Starting {settings.PROJECT_NAME} in {settings.ENVIRONMENT} mode.")

    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        description="Autonomous Self-Healing DevOps Pipeline Agent API"
    )

    # Setup CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Observability
    from backend.core.telemetry import setup_telemetry
    setup_telemetry(app)

    # API Routers will be included here
    from backend.api.v1 import api_router
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    @app.get("/health")
    async def health_check():
        return {"status": "ok", "environment": settings.ENVIRONMENT}

    return app

app = create_app()
