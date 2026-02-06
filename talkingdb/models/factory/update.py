from typing import Optional, Type, Set, get_origin, get_args
from pydantic import BaseModel, create_model


def is_list_type(annotation) -> bool:
    origin = get_origin(annotation)
    return origin in (list, set)


def create_update_model(
    *,
    source_model: Type[BaseModel],
    name: str,
    exclude_fields: Set[str] = set(),

    list_mode: bool = False,
    list_only: Optional[Set[str]] = None,
    list_exclude: Optional[Set[str]] = None,
    remove_original_list_field: bool = True,
) -> Type[BaseModel]:
    """
    Create a PATCH/update model dynamically from a source Pydantic model.

    - All scalar fields become Optional
    - Excluded fields are omitted
    - List fields can be transformed into added_/removed_ fields
    """

    fields = {}

    for field_name, field_info in source_model.model_fields.items():
        if field_name in exclude_fields:
            continue

        annotation = field_info.annotation
        is_list = list_mode and is_list_type(annotation)

        if is_list:
            if list_only and field_name not in list_only:
                is_list = False
            if list_exclude and field_name in list_exclude:
                is_list = False

        if is_list:
            # extract List[T]
            item_type = get_args(annotation)[0]

            fields[f"added_{field_name}"] = (
                Optional[list[item_type]],
                None,
            )
            fields[f"removed_{field_name}"] = (
                Optional[list[item_type]],
                None,
            )

            if not remove_original_list_field:
                fields[field_name] = (Optional[annotation], None)
        else:
            fields[field_name] = (Optional[annotation], None)

    return create_model(name, **fields)


def apply_patch(target: dict, patch: dict):

    for key, value in patch.items():
        if key.startswith(("added_", "removed_")):
            continue
        target[key] = value

    for key, value in patch.items():
        if key.startswith("added_"):
            field = key.removeprefix("added_")
            target.setdefault(field, [])

            for item in value:
                if item not in target[field]:
                    target[field].append(item)

        elif key.startswith("removed_"):
            field = key.removeprefix("removed_")
            target.setdefault(field, [])

            target[field] = [
                item for item in target[field] if item not in value
            ]
