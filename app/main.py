import os

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import Base, engine

os.makedirs(settings.upload_dir, exist_ok=True)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="API for document-based AI assistant",
    version="0.1.0"
)

app.include_router(api_router)