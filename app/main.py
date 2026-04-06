import os

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings

os.makedirs(settings.upload_dir, exist_ok=True)

app = FastAPI(
    title=settings.app_name,
    description="API for document-based AI assistant",
    version="0.1.0"
)

app.include_router(api_router)