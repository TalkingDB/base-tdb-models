import json
from typing import Any, Dict, Optional, ClassVar, Set, Union
from pydantic import BaseModel, ConfigDict


class Metadata(BaseModel):
    scope: Optional[str] = None
    event_group_id: Optional[str] = None
    trigger_event_id: Optional[str] = None

    model_config = ConfigDict(extra="allow")

    _fields: ClassVar[Set[str]] = {
        "scope",
        "event_group_id",
        "trigger_event_id",
    }

    @classmethod
    def from_json(cls, value: str) -> Optional["Metadata"]:
        try:
            data = json.loads(value)
        except Exception:
            return None

        if not isinstance(data, dict):
            return None

        if not data:
            return None

        return cls(**data)

    def to_json(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")

    def to_str(self) -> str:
        return json.dumps(self.model_dump(mode="json"))

    @classmethod
    def ensure_metadata(cls, value: Optional["Metadata"]) -> "Metadata":
        return value or cls(
            scope="org",
            event_group_id="",
            trigger_event_id="",
        )

    def extend_metadata(
        self,
        value: Union[str, Dict[str, Any]],
        *,
        overwrite: bool = False,
    ) -> "Metadata":
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except Exception:
                return self

        if not isinstance(value, dict) or not value:
            return self

        updates: Dict[str, Any] = {}

        for k, v in value.items():
            current = getattr(self, k, None)

            if overwrite or current in (None, ""):
                updates[k] = v

        if not updates:
            return self

        return self.model_copy(update=updates)

    def core_fields(self) -> Dict[str, Any]:
        return {k: getattr(self, k) for k in self._fields}

    def extra_fields(self) -> Dict[str, Any]:
        return {
            k: v
            for k, v in self.model_dump().items()
            if k not in self._fields
        }


DEFAULT_METADATA = '{"scope": "org", "event_group_id": "", "trigger_event_id": ""}'
