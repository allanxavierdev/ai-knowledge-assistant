from datetime import datetime
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    original_name: str
    stored_name: str
    content_type: str
    size_bytes: int
    status: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }