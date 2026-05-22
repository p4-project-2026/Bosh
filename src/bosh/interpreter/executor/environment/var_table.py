from .table import Table
from typing import Dict, Optional
from bosh.helper_functions.logged import logged, LogCase
class VarTable(Table[int]):
    

    @logged(
        start=lambda self, name, address: (
            f"Attempting to bind variable '{name}' to address {address} in current scope..."
        ),
        success={
            "success": lambda self, name, address: (
                f"Variable '{name}' bound to address {address} in current scope successfully."
            )
        }
    )
    def bind(self, name: str, address: int, *, log_case: LogCase):
        if name in self.table:
            raise Exception(f"Variable '{name}' already defined in scope.")
        
        log_case.set("success")
        self.table[name] = address
    
    @logged(
        start=lambda self, name: (
            f"Attempting to look up variable '{name}' in current scope..."
        ),
        success={ 
            "success": lambda self, name: (
                f"Variable '{name}' found in current scope."
            )
        }
    )
    def lookup(self, name: str, *, log_case: LogCase) -> int:
        if name in self.table:
            return self.table[name]
        
        raise Exception(f"Variable '{name}' not found in scope.")