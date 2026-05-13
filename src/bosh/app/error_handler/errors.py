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
    def __init__(self, message: str, node: Optional[ast.AST] = None, severity: str = "error", details: Optional[Dict[str, Any]] = None, suggestion: Optional[str] = None, cause: Optional[Error] = None, color: Optional[str] = None):
        formatted_message = f"Error in \"{node.pos.filename}\" a line {node.pos.line}\n{get_line(node.pos.line)}"
        pos = f" (line {node.lineno}, column {node.col_offset})" if node and hasattr(node, 'lineno') and hasattr(node, 'col_offset') else ""
        formatted_message += pos
        super().__init__(message=formatted_message, severity=severity, details=details, suggestion=suggestion, cause=cause, color=color)