
import re
import html
from dataclasses import dataclass, field
from typing import List, Optional
from html.parser import HTMLParser
from copy import deepcopy
from ....utils.dataclass import from_dict_safe


def make_id(parent_id: str, kind: str, index: int) -> str:
    return f"{parent_id}:{kind}::{index}"


@dataclass(eq=True)
class RunAttributes:
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    underline: Optional[bool] = None
    font_size: Optional[float] = None
    font_name: Optional[str] = None
    font_color: Optional[str] = None  # hex string, e.g., '000000'
    subscript: Optional[bool] = None
    superscript: Optional[bool] = None
    case: Optional[str] = None  # 'upper', 'capitalize', 'sentence'
    styles: Optional[List[str]] = None
    comment_ids: Optional[List[str]] = None
    comment_text: Optional[str] = None
    tracked_change: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "RunAttributes":
        return from_dict_safe(cls, data)


@dataclass
class RunModel:
    text: str
    attributes: RunAttributes = field(default_factory=RunAttributes)
    type: str = "Run"
    id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "RunModel":
        if data.get("attributes") is not None:
            data["attributes"] = RunAttributes.from_dict(data["attributes"])

        return from_dict_safe(cls, data)

    def assign_ids(self, parent_id: str, index: int):
        self.id = make_id(parent_id, "run", index)

    def to_text(self, mode="full") -> str:
        attrs = self.attributes or RunAttributes()

        if mode == "full":
            return self.text
        elif mode == "wrap":
            if attrs.subscript:
                return f"<sub>{self.text}</sub>"
            if attrs.superscript:
                return f"<sup>{self.text}</sup>"
        elif mode == "drop":
            if attrs.subscript or attrs.superscript:
                return ""
            else:
                return self.text

        return self.text

    def to_html(self) -> str:
        """
        Render this run as HTML using RunAttributes only.
        """
        if not self.text:
            return ""

        wrapped = html.escape(self.text)
        attrs = self.attributes or RunAttributes()

        # ---------------------
        # Build CSS styles
        # ---------------------
        styles = []

        if attrs.font_size:
            styles.append(f"font-size: {attrs.font_size}pt")

        if attrs.font_name:
            styles.append(f"font-family: '{attrs.font_name}'")

        if attrs.font_color:
            styles.append(f"color: #{attrs.font_color}")

        if attrs.underline:
            styles.append("text-decoration: underline")

        if attrs.case:
            case_map = {
                "upper": "uppercase",
                "capitalize": "capitalize",
                "sentence": "none",
            }
            if attrs.case in case_map:
                styles.append(f"text-transform: {case_map[attrs.case]}")

        style_attr = f' style="{"; ".join(styles)}"' if styles else ""

        # ---------------------
        # Build HTML attributes
        # ---------------------
        html_attrs = []

        if attrs.styles:
            html_attrs.append(f'class="{" ".join(attrs.styles)}"')

        if attrs.comment_ids:
            html_attrs.append(
                f'data-comments="{" ".join(attrs.comment_ids)}"')

        if attrs.tracked_change:
            html_attrs.append(f'data-track="{attrs.tracked_change}"')

        attr_str = " " + " ".join(html_attrs) if html_attrs else ""

        # ---------------------
        # Tag wrapping order
        # ---------------------

        if attrs.bold:
            wrapped = f"<strong>{wrapped}</strong>"

        if attrs.italic:
            wrapped = f"<em>{wrapped}</em>"

        if attrs.subscript:
            wrapped = f"<sub>{wrapped}</sub>"

        if attrs.superscript:
            wrapped = f"<sup>{wrapped}</sup>"

        # Final span wrapper
        return f"<span{style_attr}{attr_str}>{wrapped}</span>"

    def get_color(self) -> Optional[str]:
        attrs = self.attributes
        if not attrs:
            return None

        if attrs.font_color:
            return attrs.font_color.upper()

        if attrs.styles:
            for s in attrs.styles:
                m = re.match(r"color:([0-9A-Fa-f]{6})", s)
                if m:
                    return m.group(1).upper()

        return None

    @staticmethod
    def from_text(text: str) -> "RunModel":
        return RunModel(text=text)

    @staticmethod
    def from_html(html_text: str) -> list["RunModel"]:
        parser = _RunHTMLParser()
        parser.feed(html_text)
        return parser.runs

    @staticmethod
    def slice_run(run: "RunModel", start: int, end: int) -> Optional["RunModel"]:
        if start < 0 or end > len(run.text) or start >= end:
            return None

        return RunModel(
            text=run.text[start:end],
            attributes=deepcopy(run.attributes)
        )

    @staticmethod
    def split_run(run: "RunModel", start: int, end: int) -> tuple[Optional["RunModel"], Optional["RunModel"], Optional["RunModel"]]:

        before = RunModel.slice_run(run, 0, start)
        middle = RunModel.slice_run(run, start, end)
        after = RunModel.slice_run(run, end, len(run.text))

        return before, middle, after

    @staticmethod
    def merge_attributes(runs: list["RunModel"]) -> RunAttributes:

        if not runs:
            return RunAttributes()

        base = deepcopy(runs[0].attributes)

        for r in runs[1:]:
            for field in base.__dataclass_fields__:
                if getattr(base, field) != getattr(r.attributes, field):
                    setattr(base, field, None)

        return base

    @staticmethod
    def find_run_window(runs: list["RunModel"], text: str) -> Optional[dict]:
        texts = [r.text for r in runs]
        n = len(runs)

        for w in range(1, n + 1):
            for i in range(0, n - w + 1):
                merged = "".join(texts[i:i + w])
                idx = merged.find(text)
                if idx != -1:
                    return {
                        "start_run": i,
                        "end_run": i + w,
                        "char_start": idx,
                        "char_end": idx + len(text),
                        "merged_text": merged,
                    }

        return None

    @staticmethod
    def drop_text(runs: list["RunModel"], text: str) -> list["RunModel"]:

        win = RunModel.find_run_window(runs, text)
        if not win:
            return runs

        sr, er = win["start_run"], win["end_run"]
        cs, ce = win["char_start"], win["char_end"]

        merged = runs[sr:er]
        out: list[RunModel] = []

        out.extend(deepcopy(runs[:sr]))

        offset = 0
        for r in merged:
            r_len = len(r.text)
            r_start = max(0, cs - offset)
            r_end = min(r_len, ce - offset)

            before, _, after = RunModel.split_run(r, r_start, r_end)

            if before:
                out.append(before)
            if after:
                out.append(after)

            offset += r_len

        out.extend(deepcopy(runs[er:]))

        return out

    @staticmethod
    def replace_text(runs: list["RunModel"], text: str, html: str, comment_text: Optional[str] = None) -> list["RunModel"]:

        win = RunModel.find_run_window(runs, text)
        if not win:
            return runs

        sr, er = win["start_run"], win["end_run"]
        cs, ce = win["char_start"], win["char_end"]

        merged = runs[sr:er]

        out: list[RunModel] = []

        out.extend(deepcopy(runs[:sr]))

        offset = 0
        before_parts = []
        del_parts = []
        after_parts = []

        for r in merged:
            r_len = len(r.text)
            r_start = max(0, cs - offset)
            r_end = min(r_len, ce - offset)

            before, middle, after = RunModel.split_run(r, r_start, r_end)

            if before:
                before_parts.append(before)

            if middle:
                middle.attributes.tracked_change = "del"
                del_parts.append(middle)

            if after:
                after_parts.append(after)

            offset += r_len

        out.extend(before_parts)
        out.extend(del_parts)

        inserted = RunModel.from_html(html)
        first_ins = True
        for r in inserted:
            r.attributes.tracked_change = "ins"
            if first_ins and comment_text:
                r.attributes.comment_text = comment_text
                first_ins = False
            out.append(r)

        out.extend(after_parts)

        out.extend(deepcopy(runs[er:]))

        return out


class _RunHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.runs: list[RunModel] = []
        self.stack: list[RunAttributes] = [RunAttributes()]

    def handle_starttag(self, tag, attrs):
        parent = self.stack[-1]
        current = deepcopy(parent)

        if tag == "strong":
            current.bold = True
        elif tag == "em":
            current.italic = True
        elif tag == "sub":
            current.subscript = True
        elif tag == "sup":
            current.superscript = True
        elif tag == "span":
            attr_map = dict(attrs)
            if "class" in attr_map:
                current.styles = attr_map["class"].split()
            if "style" in attr_map:
                self._parse_style(attr_map["style"], current)

        self.stack.append(current)

    def handle_endtag(self, tag):
        if len(self.stack) > 1:
            self.stack.pop()

    def handle_data(self, data):
        if not data:
            return

        self.runs.append(
            RunModel(
                text=data,
                attributes=deepcopy(self.stack[-1])
            )
        )

    def _parse_style(self, style: str, attrs: RunAttributes):
        for rule in style.split(";"):
            if ":" not in rule:
                continue
            key, value = map(str.strip, rule.split(":", 1))

            if key == "font-size" and value.endswith("pt"):
                attrs.font_size = float(value[:-2])
            elif key == "font-family":
                attrs.font_name = value.strip("'\"")
            elif key == "color" and value.startswith("#"):
                attrs.font_color = value[1:]
            elif key == "text-decoration" and "underline" in value:
                attrs.underline = True
            elif key == "text-transform":
                reverse = {
                    "uppercase": "upper",
                    "capitalize": "capitalize",
                }
                attrs.case = reverse.get(value)
