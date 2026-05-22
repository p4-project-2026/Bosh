from contextlib import contextmanager
from os import name
from typing import Dict, Generic, Optional, TypeVar

from bosh.helper_functions.logged import logged, LogCase

T = TypeVar('T')

class Table(Generic[T]):
    def __init__(self, function_scope: bool = False, table: Optional[Dict[str, T]] = None):
        self.table: Dict[str, T] = {} if table is None else table.copy()
        self.function_scope: bool = function_scope

    @logged(
            start=lambda self, name, value: (
                f"Attempting to bind name '{name}' to value {value} in current scope..."
        ),
        success={
            "success": lambda self, name, value: (
                f"Name '{name}' bound to value {value} in current scope successfully."
            )
        }
    )
    def bind(self, name: str, value: T, *, log_case: LogCase) -> None:
        if name in self.table:
            raise Exception(f"Name '{name}' already defined in scope.")
            
        self.table[name] = value
        log_case.set("success")


    @logged(
        start=lambda self, name: (
            f"Looking up name '{name}' in current scope..."
        ),
        success={
            "success": lambda self, name, value: (
                f"Name '{name}' found in current scope with value {value}."
            )
        }
    )
    def lookup(self, name: str, *, log_case: LogCase) -> T:
        
        if name in self.table:
            value = self.table[name]
            log_case.set("success", value=value)
            return value
        
        raise Exception(f"Name '{name}' not found in scope.")


    @logged(
        start=lambda self, name: (
            f"Checking if name '{name}' is contained in current scope..."
        ),
        success={
            "contains": lambda self, name: (
                f"Name '{name}' is contained in current scope."
            ),
            "not_contains": lambda self, name: (
                f"Name '{name}' is not contained in current scope."
            )
        }
    )
    def contains(self, name: str, *, log_case: LogCase) -> bool:
            result = name in self.table
            
            log_case.set("contains") if result else log_case.set("not_contains")
            
            return result
    
    
    @logged(
        start=lambda self: (
            f"Computing domain of current scope..."
        ),
        success={
            "success": lambda self, domain: (
                f"Domain of current scope computed successfully. Domain: {domain}"
            )
        }
    )
    def domain(self, *, log_case: LogCase) -> list[str]:
        names = list(self.table.keys())
        log_case.set("success", domain=names)
        return names
    

    @logged(
        start=lambda self: (
            f"Computing snapshot of current scope..."
        ),
        success={
            "success": lambda self, snapshot: (
                f"Snapshot of current scope computed successfully. Snapshot: {snapshot}"
            )
        }
    )
    def get_snapshot(self, *, log_case: LogCase) -> Dict[str, T]:
        snapshot = self.table.copy()
        log_case.set("success", snapshot=snapshot)
        return snapshot
    

    @logged(
        start=lambda self, function_scope = None: (
            f"Creating copy of current scope with function_scope={function_scope}..."
        ),
        success={
            "success": lambda self, function_scope = None,* , actual_function_scope: (
                f"Copy of current scope created successfully with function_scope={actual_function_scope}."
            )
        }
    )
    def copy(self, function_scope: Optional[bool] = None, *, log_case: LogCase) -> "Table[T]":
        copy_table = self.__class__(
            function_scope=self.function_scope if function_scope is None else function_scope,
            table=self.table.copy()
        )
        log_case.set("success", actual_function_scope=copy_table.function_scope)
        return copy_table