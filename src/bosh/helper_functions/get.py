from bosh.interpreter.interpreter import Interpreter

def get_code() -> str:
    if not Interpreter.code:
        return ""
    return Interpreter.code

def get_line(line_number: int) -> str:
    code = get_code()
    if not code:
        return ""
    lines = code.splitlines()
    if line_number < 1 or line_number > len(lines):
        return ""
    return lines[line_number - 1]