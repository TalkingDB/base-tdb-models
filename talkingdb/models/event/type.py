from enum import Enum


class EventType(str, Enum):
    CONTENT_ELEMENT = "CONTENT_ELEMENT"
    GRAPH_INDEX = "GRAPH_INDEX"
