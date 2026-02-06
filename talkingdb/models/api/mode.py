from enum import Enum


class ClientMode(str, Enum):
    API = "api"
    DIRECT = "direct"
