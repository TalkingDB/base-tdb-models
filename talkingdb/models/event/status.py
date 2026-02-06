from enum import Enum


class EventStatus(str, Enum):
    CREATED = "created"
    ONGOING = "ongoing"
    COMPLETED = "completed"
