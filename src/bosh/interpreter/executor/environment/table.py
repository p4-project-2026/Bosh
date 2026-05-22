from contextlib import contextmanager
from typing import Dict, Generic, Optional, TypeVar

from bosh.helper_functions.logged import logged, LogCase

T = TypeVar('T')

class Table(Generic[T]):
    def __init__(self, function_scope: bool = False, table: Optional[Dict[str, T]] = None):
        self.table: Dict[str, T] = {} if table is None else table.copy()
        self.function_scope: bool = function_scope


    def log(self, message: str) -> None:
        vvvprint(f"{self.__class__.__name__}: {message}")

    @contextmanager
    def step(self, start: str, success: str):
        self.log(start)
        try:
            yield
        except Exception as e:
            self.log(f"Failed: {e}")
            raise
        self.log(success)

    def bind(self, name: str, value: T):
        with self.step(f"Attempting to bind name '{name}' to value {value} in current scope...", f"Name '{name}' bound to value {value} in current scope."):
            if name in self.table:
                raise Exception(f"Name '{name}' already defined in scope.")
            self.table[name] = value
    
    @logged(
        start=lambda self, name: f"looking up name '{name}' in current scope...",
        success={
            "success": lambda self, result, name: 
            f"Name '{name}' found in current scope with value {result}.",
        },
    )
    def lookup(self, name: str, *, log_case: LogCase) -> T:
        
        if name in self.table:
            value = self.table[name]
            log_case.set("success", result=value, name=name)
            return value
        raise Exception(f"Name '{name}' not found in scope.")

    
    def contains(self, name: str) -> bool:
        with self.step(f"Checking if name '{name}' exists in current scope...", f"Name '{name}' {'exists' if name in self.table else 'does not exist'} in current scope."):
            return name in self.table

    def domain(self) -> list[str]:
        with    self.step(f"Retrieving domain of current scope...", f"Domain of current scope retrieved successfully. Names in domain: {list(self.table.keys())}"):
            return list(self.table.keys())
    
    def get_snapshot(self) -> Dict[str, T]:
        with self.step(f"Creating snapshot of current scope...", f"Snapshot of current scope created successfully. Snapshot: {self.table}"):
            return self.table.copy()
    
    def copy(self, function_scope: Optional[bool] = None):
        with self.step(f"Creating copy of current table with function_scope={function_scope}...", f"Copy of current table created successfully with function_scope={function_scope}."):
            return self.__class__(
                function_scope=self.function_scope if function_scope is None else function_scope,
                table=self.table.copy()
            )