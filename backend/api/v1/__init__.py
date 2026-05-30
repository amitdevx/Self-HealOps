from fastapi import APIRouter
from backend.api.v1 import auth, incidents, webhooks, actions, analyses, validations

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
api_router.include_router(actions.router, prefix="/actions", tags=["actions"])
api_router.include_router(analyses.router, prefix="/analyses", tags=["analyses"])
api_router.include_router(validations.router, prefix="/validations", tags=["validations"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
