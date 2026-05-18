from typing import Optional, Dict, List, TypeVar, TYPE_CHECKING

from bosh.interpreter.executor.environment.table import Table
if TYPE_CHECKING:
    from bosh.interpreter.abstract_syntax.ast_definitions import TaskDecl


from dataclasses import dataclass
T = TypeVar('T')

@dataclass
class FunctionSignature:
    
    param: List[str]
    param_types: Dict[str, set[str]]
    return_type: Optional[set[str]]

    function_def: "TaskDecl"
    
    def __init__(self, parameters: Dict[str, set[str]], return_type: Optional[set[str]] = None, function_def: "TaskDecl" = None):
        self.param = list(parameters.keys())
        self.param_types = parameters
        self.return_type = return_type if return_type is not None else set()
        self.function_def = function_def

class FuncTable(Table[FunctionSignature]):
    
    def bind(self, name: str, signature: FunctionSignature):
        vvvprint(f"FuncTable: Attempting to bind function '{name}' with signature {signature} in current scope...")
        if name in self.table:
            if self.table[name].function_def is not signature.function_def:
                raise Exception(f"Function '{name}' already defined in scope with a different definition.")
        vvvprint(f"FuncTable: Binding function '{name}' with signature {signature} in current scope...")
        self.table[name] = signature
        vvvprint(f"FuncTable: Function '{name}' bound successfully.")

    def lookup(self, name: str) -> FunctionSignature:
        vvvprint(f"FuncTable: Looking up function '{name}' in current scope...")
        if name in self.table:
            vvvprint(f"FuncTable: Function '{name}' found in current scope with signature {self.table[name]}.")
            return self.table[name]
        raise Exception(f"Function '{name}' not found in scope.")
    
    
    


    