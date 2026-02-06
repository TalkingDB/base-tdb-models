from uuid import uuid4
from pydantic import BaseModel, EmailStr
from smart_slugify import slugify


class EventModel(BaseModel):
    scope: str
    event_id: str
    event_type: str
    event_data: dict
    event_status: str
    event_group_id: str
    trigger_event_id: str
    user_email: EmailStr

    @staticmethod
    def make_id(event_id: str) -> str:
        if event_id.startswith("event::"):
            return event_id
        return f"event::{slugify(event_id)}"

    @staticmethod
    def ensure_id(is_id) -> str:
        return is_id if is_id else str(uuid4())
