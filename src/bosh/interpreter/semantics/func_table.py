from typing import Optional, Dict, List, TypeVar, TYPE_CHECKING
from bosh.helper_functions.logged import logged, LogCase

from bosh.interpreter.executor.environment.table import Table
if TYPE_CHECKING:
    from bosh.interpreter.abstract_syntax.ast_definitions import TaskDecl



T = TypeVar('T')


class FunctionSignature:
    
    param: List[str]
    param_types: Dict[str, set[str]]
    return_type: Optional[set[str]]

    function_def: "TaskDecl"
    first_check: bool = False,
    called_during_first_check = False
    
    def __init__(self, parameters: Dict[str, set[str]], function_def: "TaskDecl" , return_type: Optional[set[str]] = {"UNKNOWN"}, first_check: bool = False):
        self.param = list(parameters.keys())
        self.param_types = parameters
        self.return_type = return_type
        self.function_def = function_def
        self.first_check = first_check
        self.called_during_first_check = False


class FuncTable(Table[FunctionSignature]):
    
    @logged(
        start=lambda self, name, signature: (
            f"Attempting to bind function '{name}' with signature {signature} in current scope..."
        ),
        success={
            "success": lambda self, name, signature: (
                f"Function '{name}' bound to signature {signature} in current scope successfully."
            )
        }
    )
    def bind(self, name: str, signature: FunctionSignature, log_case: LogCase):
        if name in self.table:
            if self.table[name].function_def is not signature.function_def:
                raise Exception(f"Function '{name}' already defined in scope with a different definition.")
        self.table[name] = signature
        log_case.set("success")


    @logged(
        start=lambda self, name: (
            f"Attempting to look up function '{name}' in current scope..."
        ),
        success={
            "success": lambda self, name, signature: (
                f"Function '{name}' found in current scope with signature {signature}."
            )
        }
    )
    def lookup(self, name: str, log_case: LogCase) -> FunctionSignature:
        if name in self.table:
            function_signature = self.table[name]
            log_case.set("success", signature=function_signature)
            return function_signature
        raise Exception(f"Function '{name}' not found in scope.")
    
    
    


    