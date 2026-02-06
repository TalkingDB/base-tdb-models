
from dataclasses import dataclass, field
from typing import List, Optional
from ..elements.base.base import make_id, RunModel
from ..elements.element import ElementModel, ParagraphModel, TableModel
from ..placeholders.placeholder import PlaceholderModel
from ..elements.primitive.paragraph import build_comment_text
from ...utils.dataclass import from_dict_safe


@dataclass
class HeaderModel:
    runs: List[RunModel] = field(default_factory=list)
    type: str = "Header"
    id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "HeaderModel":
        data["runs"] = [
            RunModel.from_dict(run)
            for run in data.get("runs", [])
        ]

        return from_dict_safe(cls, data)

    def assign_ids(self, parent_id: str, index: int):
        self.id = make_id(parent_id, "header", index)
        for i, run in enumerate(self.runs):
            run.assign_ids(self.id, i)

    def to_text(self, mode="full") -> str:
        return "".join(r.to_text(mode) or "" for r in self.runs)

    def to_html(self) -> str:
        inner_html = "".join(
            r.to_html() for r in self.runs if r.to_text()
        )

        if not inner_html:
            inner_html = "&nbsp;"

        return f"<header>{inner_html}</header>"

    def apply_inline_placeholder(self, ph: PlaceholderModel) -> bool:
        if not ph.replaced_text:
            return False

        full_text = self.to_text(mode="full")
        if ph.text not in full_text:
            return False

        comment_text = build_comment_text(ph)

        self.runs = RunModel.replace_text(
            self.runs,
            ph.text,
            ph.replaced_text,
            comment_text=comment_text,
        )
        return True

    def apply_deleted_placeholder(self, ph: PlaceholderModel):
        full_text = self.to_text()
        if ph.text not in full_text:
            return False

        self.runs = RunModel.drop_text(
            self.runs,
            ph.text,
        )
        return True


@dataclass
class FooterModel:
    runs: List[RunModel] = field(default_factory=list)
    type: str = "Footer"
    id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "FooterModel":
        data["runs"] = [
            RunModel.from_dict(run)
            for run in data.get("runs", [])
        ]
        return from_dict_safe(cls, data)

    def assign_ids(self, parent_id: str, index: int):
        self.id = make_id(parent_id, "footer", index)
        for i, run in enumerate(self.runs):
            run.assign_ids(self.id, i)

    def to_text(self, mode="full") -> str:
        return "".join(r.to_text(mode) or "" for r in self.runs)

    def to_html(self) -> str:
        inner_html = "".join(
            r.to_html() for r in self.runs if r.to_text()
        )

        if not inner_html:
            inner_html = "&nbsp;"

        return f"<footer>{inner_html}</footer>"

    def apply_inline_placeholder(self, ph: PlaceholderModel) -> bool:
        if not ph.replaced_text:
            return False

        full_text = self.to_text(mode="full")
        if ph.text not in full_text:
            return False

        comment_text = build_comment_text(ph)

        self.runs = RunModel.replace_text(
            self.runs,
            ph.text,
            ph.replaced_text,
            comment_text=comment_text,
        )
        return True

    def apply_deleted_placeholder(self, ph: PlaceholderModel):
        full_text = self.to_text()
        if ph.text not in full_text:
            return False

        self.runs = RunModel.drop_text(
            self.runs,
            ph.text,
        )
        return True


@dataclass
class LayoutModel:
    orientation: str  # 'PORTRAIT' or 'LANDSCAPE'
    header: Optional[HeaderModel] = None
    footer: Optional[FooterModel] = None
    elements: List[ElementModel] = field(default_factory=list)
    type: str = "Layout"
    id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "LayoutModel":
        if data.get("header") is not None:
            data["header"] = HeaderModel.from_dict(data["header"])

        if data.get("footer") is not None:
            data["footer"] = FooterModel.from_dict(data["footer"])

        def element_from_dict(data: dict) -> ElementModel:
            if data.get("type") == "Paragraph":
                return ParagraphModel.from_dict(data)

            if data.get("type") == "Table":
                return TableModel.from_dict(data)

        data["elements"] = [
            element_from_dict(el)
            for el in data.get("elements", [])
        ]

        return from_dict_safe(cls, data)

    def assign_ids(self, parent_id: str, index: int):
        self.id = make_id(parent_id, "layout", index)

        if self.header:
            self.header.assign_ids(self.id, 0)

        if self.footer:
            self.footer.assign_ids(self.id, 0)

        for i, elem in enumerate(self.elements):
            elem.assign_ids(self.id, i)
