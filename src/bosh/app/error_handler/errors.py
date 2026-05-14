from pyparsing import line

from bosh.helper_functions.paths import PathsHelper
from pathlib import Path

from .error_handlers import *

class RunTypeError(Error):
    def __init__(self, message: str, severity: str = "error", details: Optional[Dict[str, Any]] = None, suggestion: Optional[str] = None, cause: Optional[Error] = None, color: Optional[str] = None):
        formatted_message = f"File \"{get_call_location()}\" Run Type Error: {message}"
        super().__init__(message=formatted_message, severity=severity, details=details, suggestion=suggestion, cause=cause, color=color)

class CLIError(Error):
    def __init__(self, message: str, severity: str = "error", details: Optional[Dict[str, Any]] = None, suggestion: Optional[str] = None, cause: Optional[Error] = None, color: Optional[str] = None):
        formatted_message = f"File \"{get_call_location()}\" CLI Error: {message}"
        super().__init__(message=formatted_message, severity=severity, details=details, suggestion=suggestion, cause=cause, color=color)

class ArgumentError(Error):
    def __init__(self, message: str, severity: str = "error", details: Optional[Dict[str, Any]] = None, suggestion: Optional[str] = None, cause: Optional[Error] = None, color: Optional[str] = None):
        formatted_message = f"File \"{get_call_location()}\" Argument Error: {message}"
        super().__init__(message=formatted_message, severity=severity, details=details, suggestion=suggestion, cause=cause, color=color)

class ConfigurationError(Error):
    def __init__(self, message: str, severity: str = "error", details: Optional[Dict[str, Any]] = None, suggestion: Optional[str] = None, cause: Optional[Error] = None, color: Optional[str] = None):
        formatted_message = f"File \"{get_call_location()}\" Configuration Error: {message}"
        super().__init__(message=formatted_message, severity=severity, details=details, suggestion=suggestion, cause=cause, color=color)

class BoshTypeError(Error):
    def __init__(self, message: str, node: Optional[ast.AST] = None, severity: str = "error", details: Optional[Dict[str, Any]] = None, suggestion: Optional[str] = None, cause: Optional[Error] = None, color: Optional[str] = None):
        formatted_message = f"File \"{get_call_location()}\" Bosh Type Error: {message}"
        super().__init__(message=formatted_message, severity=severity, details=details, suggestion=suggestion, cause=cause, color=color)

class BoshRuntimeError(Error):
    def __init__(self, message: str, node: Optional[ast.AST] = None, severity: str = "error", details: Optional[Dict[str, Any]] = None, suggestion: Optional[str] = None, cause: Optional[Error] = None, color: Optional[str] = None):
        formatted_message = f"File \"{get_call_location()}\" Bosh Runtime Error: {message}"
        pos = f" (line {node.lineno}, column {node.col_offset})" if node and hasattr(node, 'lineno') and hasattr(node, 'col_offset') else ""
        formatted_message += pos
        super().__init__(message=formatted_message, severity=severity, details=details, suggestion=suggestion, cause=cause, color=color)

class BoshScriptError(Error):
    def __init__(self, message: str, severity: str = "error", details: Optional[Dict[str, Any]] = None, suggestion: Optional[str] = None, cause: Optional[Error] = None, color: Optional[str] = None):
        super().__init__(message=message, severity=severity, details=details, suggestion=suggestion, cause=cause, color=color)

class LocationError(Error):
    def __init__(self, node: Optional[ast.AST] = None, severity: str = "error", details: Optional[Dict[str, Any]] = None, suggestion: Optional[str] = None, cause: Optional[Error] = None, color: Optional[str] = None, traceback: bool = True):
        pos = node.pos
        severity_prefix = f"[{severity.upper()}]: "
        line = get_line(pos.line)
        stripped_length = len(line) - len(line.lstrip())
        line = line.strip()
        filename = PathsHelper().get_project_root().joinpath(get_filename())
        filename = f"\"{filename}\" " if filename else ""
        cause = Error(message=cause, severity=severity)
        pointer = " " * (pos.start_col - 1 - stripped_length) + "^" * (pos.end_col - pos.start_col)
        formatted_message = f"    {severity_prefix}{filename}at line {pos.line}\n{indent(line, level=8)}\n{indent(pointer, level=8)}\n{cause.message}"
        if traceback:
            super().__init__(message=formatted_message, severity=severity, cause=cause)
        else:
            super().__init__(message=cause.message, severity=severity, cause=cause)