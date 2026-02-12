from typing import List
from pydantic import BaseModel, Field
from enum import Enum


class IndexType(str, Enum):
    OUTLINE = "section@outline"
    PARA = "section@para"
    PARA_CHUNKED = "section@chunked"
    TABLE = "table@full"
    TABLE_ROW = "table@row"
    TABLE_CELL = "table@cell"
    TABLE_HEADER = "table@header"


class IndexItem(BaseModel):
    id: str
    label: str
    index: IndexType
    child: List["IndexItem"] = Field(default_factory=list)


class FileIndexModel(BaseModel):
    id: str
    filename: str
    nodes: List[IndexItem] = Field(default_factory=list)


IndexItem.model_rebuild()
