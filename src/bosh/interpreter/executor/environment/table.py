from typing import Dict, Generic, Optional, TypeVar

T = TypeVar('T')

class Table(Generic[T]):
    def __init__(self, function_scope: bool = False, table: Optional[Dict[str, T]] = None):
        self.table: Dict[str, T] = {} if table is None else table.copy()
        self.function_scope: bool = function_scope

    def bind(self, name: str, value: T):
        vvvprint(f"{self.__class__.__name__}: Attempting to bind name '{name}' to value {value} in current scope...")
        if name in self.table:
            raise Exception(f"Name '{name}' already defined in scope.")
        vvvprint(f"{self.__class__.__name__}: Binding name '{name}' to value {value} in current scope...")
        self.table[name] = value
    
    def lookup(self, name: str) -> T:
        vvvprint(f"{self.__class__.__name__}: Looking up name '{name}' in current scope...")
        if name in self.table:
            vvvprint(f"{self.__class__.__name__}: Name '{name}' found in current scope.")
            return self.table[name]
        raise Exception(f"Name '{name}' not found in scope.")
    
    def contains(self, name: str) -> bool:
        vvvprint(f"{self.__class__.__name__}: Checking if name '{name}' exists in current scope...")
        return name in self.table
    
    def domain(self) -> list[str]:
        vvvprint(f"{self.__class__.__name__}: Retrieving domain of current scope...")
        return list(self.table.keys())
    
    def get_snapshot(self) -> Dict[str, T]:
        vvvprint(f"{self.__class__.__name__}: Creating snapshot of current scope...")
        return self.table.copy()
    
    def copy(self, function_scope: Optional[bool] = None):
        vvvprint(f"{self.__class__.__name__}: Copying current scope...")
        return self.__class__(
            function_scope=self.function_scope if function_scope is None else function_scope,
            table=self.get_snapshot()
        )