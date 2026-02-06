from typing import Optional
from .elements.primitive.paragraph import ParagraphModel
from .elements.primitive.table import TableModel
from .placeholders.placeholder import PlaceholderModel, PlaceholderFutureElement
from .mutations import ElementReplacement


def resolve_structural_replacement(
    element,
    ph: PlaceholderModel,
) -> Optional[ElementReplacement]:

    if not isinstance(element, ParagraphModel):
        return None

    if ph.future_element != PlaceholderFutureElement.TABLE:
        return None

    if not ph.replaced_text:
        return None

    table = TableModel.from_html_or_text(ph.replaced_text)
    table.parent_ref_id = element.parent_ref_id

    return ElementReplacement(
        old_element_id=element.id,
        new_elements=[table],
    )
