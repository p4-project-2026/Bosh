from dataclasses import dataclass, field
from typing import Optional, Type, Dict, Any
import inspect
import ast
from pathlib import Path


class Colors:
    red: str = '\033[91m'
    green: str = '\033[92m'
    blue: str = '\033[94m'
    cyan: str = '\033[96m'
    magenta: str = '\033[95m'
    yellow: str = '\033[93m'
    white: str = '\033[97m'
    black: str = '\033[90m'
    reset: str = '\033[0m'

class Error(Exception):
    def __init__(self, message: str, severity: str = "error", details: Optional[Dict[str, Any]] = None, suggestion: Optional[str] = None, cause: Optional['Error'] = None, color: Optional[str] = None):
        self.message = message
        self.severity = severity
        self.details = details
        self.suggestion = suggestion
        self.cause = cause
        self.color = get_default_color(color, severity)
        super().__init__(str(self))
    
    def __str__(self) -> str:
        # Format the error message with color.
        result = f"{self.color}{self.message}{Colors.reset}"
        return result


def get_call_location():
    # Get the caller's file and line number
    stack = inspect.stack()
    if len(stack) > 2:
        caller_frame = stack[2]
        filename = Path(caller_frame.filename)
        line_number = caller_frame.lineno
        return f"{filename}, at line {line_number}"
    return "Unknown location"

def get_default_color(color: Optional[str], severity: str) -> str:
    if color:
        match color.lower():
            case "red": return Colors.red
            case "green": return Colors.green
            case "blue": return Colors.blue
            case "cyan": return Colors.cyan
            case "magenta": return Colors.magenta
            case "yellow": return Colors.yellow
            case "white": return Colors.white
            case "black": return Colors.black
            case _: return Colors.reset
    else:
        match severity:
            case "error": return Colors.red
            case "warning": return Colors.yellow
            case "info": return Colors.blue
            case _: return Colors.reset