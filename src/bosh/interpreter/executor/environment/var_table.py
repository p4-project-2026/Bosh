from .table import Table
from typing import Dict, Optional

class VarTable(Table[int]):
    

 
    def bind(self, name: str, address: int):
        if name in self.table:
            raise Exception(f"Variable '{name}' already defined in scope.")
        vvvprint(f"VarTable: Binding variable '{name}' to address {address} in current scope...")
        self.table[name] = address
    
    def lookup(self, name: str) -> int:
        if name in self.table:
            vvvprint(f"VarTable: Variable '{name}' found in current scope.")
            return self.table[name]
        raise Exception(f"Variable '{name}' not found in scope.")