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
    def __init__(self, message: str, severity: str = "error", details: Optional[Dict[str, Any]] = None, suggestion: Optional[str] = None, cause: Optional[Error] = None, color: Optional[str] = None):
        formatted_message = f"File \"{get_call_location()}\" Bosh Type Error: {message}"
        super().__init__(message=formatted_message, severity=severity, details=details, suggestion=suggestion, cause=cause, color=color)

class BoshRuntimeError(Error):
    def __init__(self, message: str, node: Optional[ast.AST] = None, severity: str = "error", details: Optional[Dict[str, Any]] = None, suggestion: Optional[str] = None, cause: Optional[Error] = None, color: Optional[str] = None):
        formatted_message = f"File \"{get_call_location()}\" Bosh Runtime Error: {message}"
        super().__init__(message=formatted_message, severity=severity, details=details, suggestion=suggestion, cause=cause, color=color)
        self.node = node