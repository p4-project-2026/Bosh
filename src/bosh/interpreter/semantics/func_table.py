from typing import Optional, Dict, List, TypeVar, Generic

from bosh.interpreter.executor.environment.table import Table

from dataclasses import dataclass
T = TypeVar('T')

@dataclass
class FunctionSignature:
    param: List[str]
    param_types: Dict[str, set[str]]
    return_type: Optional[set[str]]
    
    def __init__(self, parameters: Dict[str, set[str]], return_type: Optional[set[str]] = None):
        self.param = list(parameters.keys())
        self.param_types = parameters
        self.return_type = return_type if return_type is not None else set()

class FuncTable(Table[FunctionSignature]):
    
    def bind(self, name: str, signature: FunctionSignature):
        vvvprint(f"FuncTable: Attempting to bind function '{name}' with signature {signature} in current scope...")
        if name in self.table:
            raise Exception(f"Function '{name}' already defined in scope.")
        vvvprint(f"FuncTable: Binding function '{name}' with signature {signature} in current scope...")
        self.table[name] = signature
        vvvprint(f"FuncTable: Function '{name}' bound successfully.")

    def lookup(self, name: str) -> FunctionSignature:
        vvvprint(f"FuncTable: Looking up function '{name}' in current scope...")
        if name in self.table:
            vvvprint(f"FuncTable: Function '{name}' found in current scope with signature {self.table[name]}.")
            return self.table[name]
        raise Exception(f"Function '{name}' not found in scope.")
    
    


    