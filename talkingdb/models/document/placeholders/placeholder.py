
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


def make_placeholder_id(element_id: str, index: int) -> str:
    return f"{element_id}::ph::{index}"


class PlaceholderFutureElement(str, Enum):
    PARAGRAPH = "Paragraph"
    TABLE = "Table"
    UNKNOWN = "Unknown"


class PlaceholderType(str, Enum):
    INLINE = "Inline"
    KEYVALUE = "KeyValue"
    TABLECELL = "TableCell"
    HEADING = "Heading"
    CAPTION = "Caption"
    PARAGRAPH = "Paragraph"


class PlaceholderStatus(str, Enum):
    MATCHING_PENDING = "MatchingPending"
    MATCHES_FOUND = "MatchesFound"
    MATCHES_NOT_FOUND = "MatchesNotFound"
    REPLACEMENT_PENDING = "ReplacementPending"
    REPLACEMENT_DONE = "ReplacementDone"
    REPLACEMENT_NOT_FOUND = "ReplacementNotFound"


class MatcherType(str, Enum):
    SME_ADD = "SME_ADD"
    SME_DROP = "SME_DROP"
    CNM_ADD = "CNM_ADD"
    PWR_DROP = "PWR_DROP"


@dataclass
class InlineContext:
    text_before: Optional[str] = None
    text_after: Optional[str] = None

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass
class KeyValueContext:
    table_caption: Optional[str] = None
    key: Optional[str] = None

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass
class TableCellContext:
    table_caption: Optional[str] = None
    header_path: Optional[List[str]] = None
    row: Optional[int] = None

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass
class ParagraphContext:
    para_before: Optional[str] = None
    para_after: Optional[str] = None

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass
class HeadingContext:
    heading: str
    level: int
    parent: Optional[dict] = None
    children: Optional[List[dict]] = None
    siblings: Optional[List[dict]] = None
    position: Optional[int] = None

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass
class TemplateText:
    instruction_text: Optional[str] = None
    example_text: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


@dataclass
class MatchedNode:
    id: str
    content: str
    index: str
    score: float
    type: MatcherType
    heading_path: List[str]
    filename: str
    prompt: Optional[str] = None
    transformed_content: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict):
        data["type"] = MatcherType(data["type"])
        return cls(**data)


@dataclass(kw_only=True)
class PlaceholderBaseModel:
    id: str
    text: str
    status: PlaceholderStatus = PlaceholderStatus.MATCHING_PENDING
    replaced_text: Optional[str] = None
    replaced_reference: Optional[List[str]] = None
    replaced_comment: Optional[str] = None
    deleted: Optional[bool] = False

    @classmethod
    def _hydrate_base(cls, data: dict):
        data["status"] = PlaceholderStatus(data["status"])


@dataclass(kw_only=True)
class PlaceholderMappingModel:
    template_text: Optional[TemplateText] = None
    source_instruction: List[str] = field(default_factory=list)
    writing_instruction: List[str] = field(default_factory=list)
    matches: List[MatchedNode] = field(default_factory=list)

    @classmethod
    def _hydrate_mapping(cls, data: dict):
        if "template_text" in data and data["template_text"]:
            data["template_text"] = TemplateText.from_dict(
                data["template_text"])

        if "matches" in data:
            data["matches"] = [
                MatchedNode.from_dict(m) for m in data["matches"]
            ]


@dataclass(kw_only=True)
class PlaceholderContextModel:
    inline_data: Optional[InlineContext] = None
    keyvalue: Optional[KeyValueContext] = None
    tablecell: Optional[TableCellContext] = None
    paragraph: Optional[ParagraphContext] = None
    heading_info: Optional[HeadingContext] = None

    @classmethod
    def _hydrate_context(cls, data: dict):
        if "inline_data" in data and data["inline_data"]:
            data["inline_data"] = InlineContext.from_dict(data["inline_data"])

        if "keyvalue" in data and data["keyvalue"]:
            data["keyvalue"] = KeyValueContext.from_dict(data["keyvalue"])

        if "tablecell" in data and data["tablecell"]:
            data["tablecell"] = TableCellContext.from_dict(data["tablecell"])

        if "paragraph" in data and data["paragraph"]:
            data["paragraph"] = ParagraphContext.from_dict(data["paragraph"])

        if "heading_info" in data and data["heading_info"]:
            data["heading_info"] = HeadingContext.from_dict(
                data["heading_info"])


@dataclass(kw_only=True)
class PlaceholderModel(PlaceholderBaseModel, PlaceholderMappingModel, PlaceholderContextModel):
    element_id: Optional[str] = None
    type: PlaceholderType = PlaceholderType.INLINE
    future_element: PlaceholderFutureElement = PlaceholderFutureElement.UNKNOWN
    dependency: Optional[List[str]] = None
    feedback_count: int = 0

    @classmethod
    def from_dict(cls, data: dict):
        cls._hydrate_base(data)

        cls._hydrate_mapping(data)

        cls._hydrate_context(data)

        data["type"] = PlaceholderType(data["type"])
        data["future_element"] = PlaceholderFutureElement(
            data["future_element"])

        return cls(**data)
