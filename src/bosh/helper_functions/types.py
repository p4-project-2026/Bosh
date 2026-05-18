from datetime import datetime

def python_type_to_bosh_type(python_type):
    type_mapping = {
        int: "number",
        float: "decimal",
        str: "text",
        bool: "boolean",
        list: "array",
        datetime: "date",
    }
    return type_mapping.get(python_type, "unknown")