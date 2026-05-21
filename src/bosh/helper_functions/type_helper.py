
from typing import Optional

EMPTY_LIST_TYPE = "list<any>"
UNKNOWN_LIST_TYPE = "list<UNKNOWN>"
SPECIAL_LIST_TYPES = {EMPTY_LIST_TYPE, UNKNOWN_LIST_TYPE}
UNKNOWN_TYPE = "UNKNOWN"
ANY_TYPE = "any"

SPECIAL_TYPES = {UNKNOWN_TYPE, ANY_TYPE}
NUMERIC_TYPES = {"number", "decimal"}

# 'make' functions for creating type sets

def make_string_list_type(types: str) -> set[str]:
    vvvprint(f"Type Helper: Making list type from string '{types}'...")
    return {f"list<{types}>"}


def make_set_list_types(types: set[str]) -> set[str]:
    vvvprint(f"Type Helper: Making list types from set '{types}'...")
    return {f"list<{t}>" for t in types}



# 'has' functions for type sets

def has_list_type(type_set: set[str]) -> bool:
    if is_unknown_type(type_set):
        return True
    return any(is_list_type(t) for t in type_set)

def has_only_list_types(type_set: set[str]) -> bool:
    return all(is_list_type(t) for t in type_set)

def has_non_list_type(type_set: set[str]) -> bool:
    # if the type set is unknown, we have to assume it could have non-list types
    if is_unknown_type(type_set):
        return True
    return any(not is_list_type(t) for t in type_set)

def has_concrete_list_type(types: set[str]) -> bool:
    return any(
        is_list_type(t)
        and t not in SPECIAL_LIST_TYPES
        for t in types
    )

def has_only_concrete_list_types(types: set[str]) -> bool:
    return all(
        is_list_type(t)
        and t not in SPECIAL_LIST_TYPES
        for t in types
    )

# 'is' functions for type sets

# list types

def can_be_list_type(types: set[str]) -> bool:
    if type_name == UNKNOWN_TYPE:
        return True
    return type_name.startswith("list<") and type_name.endswith(">")

def is_list_type(type_name: str) -> bool:
    vvvprint(f"Type Helper: Checking if type '{type_name}' is a list type...")
    return type_name.startswith("list<") and type_name.endswith(">")

def is_only_a_list_type(type_set: set[str]) -> bool:
    vvvprint(f"Type Helper: Checking if type set '{type_set}' contains only a list type...")
    return len(type_set) == 1 and is_list_type(next(iter(type_set)))

def is_only(type_set: set[str], type_name: str) -> bool:
    vvvprint(f"Type Helper: Checking if type set '{type_set}' contains only the type '{type_name}'...")
    return len(type_set) == 1 and next(iter(type_set)) == type_name

def is_empty_list_type(types: set[str]) -> bool:
    vvvprint(f"Type Helper: Checking if type set '{types}' is an empty list type...")
    return types == {EMPTY_LIST_TYPE}

def is_unknown_list_type(types: set[str]) -> bool:
    vvvprint(f"Type Helper: Checking if type set '{types}' is an unknown list type...")
    return types == {UNKNOWN_LIST_TYPE}

def is_special_list_type(types: set[str]) -> bool:
    vvvprint(f"Type Helper: Checking if type set '{types}' is a special list type...")
    return types in SPECIAL_LIST_TYPES

def is_numeric_type(types: set[str]) -> bool:
    vvvprint(f"Type Helper: Checking if type set '{types}' is a number type...")
    return types.issubset(NUMERIC_TYPES)

def is_unknown_type(types: set[str]) -> bool:
    vvvprint(f"Type Helper: Checking if type set '{types}' is an unknown type...")
    return types == {UNKNOWN_TYPE}

def is_any_type(types: set[str]) -> bool:
    vvvprint(f"Type Helper: Checking if type set '{types}' is an any type...")
    return types == {ANY_TYPE}

def is_compatible(a: set[str], b: set[str]) -> bool:
    vvvprint(f"Type Helper: Checking if types '{a}' and '{b}' are compatible...")
    return bool(narrow(a, b))

def is_a_subset(subset: set[str], superset: set[str]) -> bool:
    vvvprint(f"Type Helper: Checking if type set '{subset}' is a subset of '{superset}'...")
    return subset.issubset(superset)



#'get' function for getting the list element types from a set of types, which returns the set of element types if there are any list types in the set, and None otherwise. This is useful for inference when we have a variable that can be multiple types, some of which are list types, and we want to extract the element types for inference purposes.

def get_all_list_types(types: set[str]) -> set[str]:
    vvvprint(f"Type Helper: Getting all list types from set '{types}'...")
    if is_unknown_type(types):
        return {UNKNOWN_LIST_TYPE}
    return {t for t in types if is_list_type(t)}

def get_all_non_list_types(types: set[str]) -> set[str]:
    vvvprint(f"Type Helper: Getting all non-list types from set '{types}'...")
    if is_unknown_type(types):
        return {UNKNOWN_TYPE}
    return {t for t in types if not is_list_type(t)}

def get_list_element_types(list_type: set[str]) -> set[str]:
    vvvprint(f"Type Helper: Getting list element types from list type set '{list_type}'...")
    return_type = set()
    if is_unknown_type(list_type):
        return {UNKNOWN_TYPE}
    for t in list_type:
        if is_list_type(t):
            elem_type = t[5:-1]
            return_type.add(elem_type)
    return return_type


#'misc' functions

def narrow(a: set[str], b: set[str]) -> set[str]:
    "Yes is long but it's the best way to handle all the special cases for now. This function returns the intersection of two sets of types,"
    "but also handles the special cases for 'any' and 'UNKNOWN' types, as well as the special list types."
    "The logic is as follows: if either set is 'any', return the other set; if either set is 'UNKNOWN', return the other set;"
    "if either set is the unknown list type and the other set has a list type, return the list types from the other set; if either set is the empty list type and the other set has a concrete list type,"
    "return the list types from the other set; otherwise, return the intersection of the two sets."
    vvvprint(f"Type Helper: Narrowing types '{a}' and '{b}'...")
    if is_any_type(a):
        return b.copy()
    if is_any_type(b):
        return a.copy()
    
    if is_unknown_type(a):
        return b.copy()
    if is_unknown_type(b):
        return a.copy()
    
    if is_empty_list_type(a) and has_list_type(b):
        return get_all_list_types(b)
    if is_empty_list_type(b) and has_list_type(a):
        return get_all_list_types(a)

    if is_unknown_list_type(a) and has_concrete_list_type(b):
        return get_all_list_types(b)
    if is_unknown_list_type(b) and has_concrete_list_type(a):
        return get_all_list_types(a)
    
    return a & b

def contains(types: Optional[set[str]], target: str) -> bool:
    if types is None:
        return False
    if is_unknown_type(types):
        return True
    if is_list_type(target):
        if is_unknown_list_type(types):
            return True
    return target in types

def contains_numeric_type(types: Optional[set[str]]) -> bool:
    if types is None:
        return False
    return any(t in NUMERIC_TYPES for t in types)