from dataclasses import dataclass
from typing import List, Any


@dataclass
class ElementReplacement:
    old_element_id: str
    new_elements: List[Any]
