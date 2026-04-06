import os
import uuid

from fastapi import UploadFile

from app.core.config import settings


class StorageService:
    def __init__(self):
        os.makedirs(settings.upload_dir, exist_ok=True)

    def save_file(self, file: UploadFile) -> tuple[str, str, int]:
        extension = os.path.splitext(file.filename)[1]
        stored_name = f"{uuid.uuid4()}{extension}"
        file_path = os.path.join(settings.upload_dir, stored_name)

        content = file.file.read()

        with open(file_path, "wb") as buffer:
            buffer.write(content)

        return stored_name, file_path, len(content)

    def delete_file(self, stored_name: str) -> None:
        file_path = os.path.join(settings.upload_dir, stored_name)
        if os.path.exists(file_path):
            os.remove(file_path)

    def get_file_path(self, stored_name: str) -> str:
        return os.path.join(settings.upload_dir, stored_name)