
from typing import Optional

EMPTY_LIST_TYPE = "list<any>"
UNKNOWN_LIST_TYPE = "list<UNKNOWN>"
SPECIAL_LIST_TYPES = {EMPTY_LIST_TYPE, UNKNOWN_LIST_TYPE}
UNKNOWN_TYPE = "UNKNOWN"
ANY_TYPE = "any"

def make_list(types: str) -> set[str]:
    return {f"list<{types}>"}

def is_list_type(type_name: str) -> bool:
    return type_name.startswith("list<") and type_name.endswith(">")

def get_list_element_types(list_type: set[str]) -> Optional[set[str]]:
    return_type = set()
    for t in list_type:
        if is_list_type(t):
            elem_type = t[5:-1]
            return_type.add(elem_type)
    return return_type if return_type else None

def has_list_type(type_set: set[str]) -> bool:
    return any(is_list_type(t) for t in type_set)

def has_only_list_types(type_set: set[str]) -> bool:
    return all(is_list_type(t) for t in type_set)

def has_non_list_type(type_set: set[str]) -> bool:
    return any(not is_list_type(t) for t in type_set)

def has_concrete_list_type(types: set[str]) -> bool:
    return any(
        is_list_type(t)
        and t not in SPECIAL_LIST_TYPES
        for t in types
    )

def is_empty_list_type(types: set[str]) -> bool:
    return types == {EMPTY_LIST_TYPE}


def is_unknown_list_type(types: set[str]) -> bool:
    return types == {UNKNOWN_LIST_TYPE}

def is_special_list_type(types: set[str]) -> bool:
    return types in SPECIAL_LIST_TYPES