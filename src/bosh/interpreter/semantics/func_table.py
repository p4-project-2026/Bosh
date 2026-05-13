from typing import Optional, Dict, List, TypeVar, Generic

from bosh.interpreter.executor.environment.table import Table

from dataclasses import dataclass
T = TypeVar('T')

@dataclass
class FunctionSignature:
    param: List[str]
    param_types: Dict[str, str]
    return_type: Optional[str] = None
    
    def __init__(self, parameters: Dict[str, str], return_type: Optional[str] = None):
        self.param = list(parameters.keys())
        self.param_types = parameters
        self.return_type = return_type

class FuncTable(Table[FunctionSignature]):
    
    def bind(self, name: str, signature: FunctionSignature):
        if name in self.table:
            raise Exception(f"Function '{name}' already defined in scope.")
        self.table[name] = signature

    def lookup(self, name: str) -> FunctionSignature:
        if name in self.table:
            return self.table[name]
        raise Exception(f"Function '{name}' not found in scope.")
    


    