


def string_format_bool(value: bool) -> str:
    return "true" if value else "false"
    
def string_format_list(value: list) -> str:
    return "[" + ", ".join(str(v) for v in value) + "]"

def string_format_list_of_bools(value: list) -> str:
    return "[" + ", ".join(string_format_bool(v) for v in value) + "]"

def string_format_list_if_strings(value: list) -> str:
    if all(isinstance(v, str) for v in value):
        return "[" + ", ".join(f'"{v}"' for v in value) + "]"
    else:
        return string_format_list(value)