from dataclasses import fields
from typing import Type, TypeVar, Dict, Any

T = TypeVar("T")


def from_dict_safe(cls: Type[T], data: Dict[str, Any]) -> T:
    allowed_keys = {f.name for f in fields(cls)}
    filtered = {k: v for k, v in data.items() if k in allowed_keys}
    return cls(**filtered)
