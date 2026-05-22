from contextlib import contextmanager

from .table import Table
from .function_binding import FunctionBinding
from typing import TypeVar, Generic, Type, Dict
from bosh.helper_functions.logged import logged, LogCase

T = TypeVar('T')


class ScopeStack(Generic[T]):
    def __init__(self, table_class: Type[Table[T]] = Table):
        self.table_class = table_class
        self.stack: list[Table[T]] = [self.table_class()]  # Start with global scope
    
    @logged(
        start=lambda self: (
            f"Creating a copy of the current scope stack..."
        ),
        success={
            "success": lambda self: (
                f"Copy of current scope stack created successfully."
            )
        }
    )
    def copy(self, log_case: LogCase):
        #deep copy the stack to ensure that modifications to the copy do not affect the original
        new_stack = ScopeStack(self.table_class)
        new_stack.stack = [scope.copy() for scope in self.stack]
        log_case.set("success")
        return new_stack


    @logged(
        start=lambda self: (
            f"Creating a new scope in the current scope stack..."
        ),
        success={
            "success": lambda self: (
                f"New scope created in current scope stack successfully."
            )
        }   
    )
    def new_scope(self, log_case: LogCase):

        self.stack.append(self.table_class())
        log_case.set("success")
        
 
    @logged(
        start=lambda self: (
            f"Attempting to exit current scope in scope stack..."
        ),        success={
            "regular_exit": lambda self: (
                f"Exited current regular scope in scope stack successfully."
            ),
            "function_scope_exit": lambda self: (
                f"Exited current function scope in scope stack successfully."
            )
        }
    )
    def exit_scope(self, log_case: LogCase):
        if len(self.stack) == 1:
            raise Exception("Cannot exit global scope.")

        if self.stack[-2].function_scope:
            self.stack.pop()  # pop function body scope
            self.stack.pop()  # pop captured function boundary scope
            log_case.set("function_scope_exit")
            return
        
        self.stack.pop()
        log_case.set("regular_exit")


    @logged(
        start=lambda self, function_def: (
            f"Attempting to enter function scope for function with parameters {function_def.parameters}..."
        ),        
        success={
            "success": lambda self, function_def: (
                f"Function scope entered successfully for function with parameters {function_def.parameters}."
            )
        }
    )

    def enter_function_scope(self, function_def: FunctionBinding, log_case: LogCase):
        function_scope = function_def.captured_scope.copy()
        function_scope.function_scope = True  # Mark the function scope
        self.stack.append(function_scope)
        self.new_scope()  # Create a new scope for the function body
        log_case.set("success")


    @logged(
        start=lambda self: (
            f"Creating snapshot of current visible scopes in scope stack..."
        ),
        success={
            "success": lambda self: (
                f"Snapshot of current visible scopes in scope stack created successfully."
            )
        }
    )


    def snapshot(self, log_case: LogCase) -> Table[T]:
        visible_scopes: list[Table[T]] = []
        for scope in reversed(self.stack):
            visible_scopes.append(scope)
            if scope.function_scope:
                break  # Stop at the first function scope

        snapshot: Dict[str, T] = {}
        for scope in reversed(visible_scopes):
            snapshot.update(scope.get_snapshot())

        snapshot_table= self.table_class(table=snapshot)
        log_case.set("success")
        return snapshot_table


    @logged(
        start=lambda self, name: (
            f"Attempting to look up variable '{name}' in current scope stack..."
        ),
        success={
            "success": lambda self, name, loc: (
                f"Variable '{name}' found in current scope stack with Store location {loc}."
            )
        }
    )
    def lookup(self, name: str, log_case: LogCase) -> T:
        for scope in reversed(self.stack):
            if scope.contains(name):
                loc = scope.lookup(name)
                log_case.set("success", loc = loc)
                return loc
            if scope.function_scope:  # If we reach a function scope or global scope, stop searching
                break
        raise Exception(f"Undefined variable '{name}'")


    @logged(
        start=lambda self, name: (
            f"Attempting to look up variable '{name}' for assignment in current scope stack..."
        ),
        success={
            "success": lambda self, name, loc: (
                f"Variable '{name}' found in current scope stack for assignment with Store location {loc}."
            )
        }
    )            
    def lookup_assign(self, name: str, log_case: LogCase) -> T:
        for scope in reversed(self.stack):
            if scope.function_scope:  # If we reach a function scope or global scope, stop searching
                break    
            if scope.contains(name):
                loc = scope.lookup(name)
                log_case.set("success", loc = loc)
                return loc
        raise Exception(f"Variable '{name}' not found in scope.")


    @logged(
        start=lambda self, name: (
            f"Checking if variable '{name}' is contained in current scope stack..."
        ),
        success={
            "contains": lambda self, name: (
                f"Variable '{name}' is contained in current scope stack."
            ),
            "not_contains": lambda self, name: (
                f"Variable '{name}' is not contained in current scope stack."
            )
        }
    )
    def contains(self, name: str, log_case: LogCase) -> bool:
        for scope in reversed(self.stack):
            if scope.contains(name):
                log_case.set("contains")
                return True
            if scope.function_scope:  # If we reach a function scope or global scope, stop searching
                break
        log_case.set("not_contains")
        return False


    @logged(
        start=lambda self, name, value: (
            f"Attempting to bind variable '{name}' to value {value} in current scope stack..."
        ),
        success={
            "success": lambda self, name, value: (
                f"Variable '{name}' bound to value {value} in current scope stack successfully."
            )
        }
    )
    def bind(self, name: str, value: T, log_case: LogCase):
        if self.stack[-1].contains(name):
            raise Exception(f"Variable '{name}' already defined in current scope.")
        
        log_case.set("success")
        self.stack[-1].bind(name, value)


    @logged(
        start=lambda self: (
            f"Retrieving domain of all visible variables in current scope stack..."
        ),
        success={
            "success": lambda self, domain: (
                f"Domain of all visible variables in current scope stack retrieved successfully. Domain: {domain}"
            )
        }
    )
    def domain(self, log_case: LogCase) -> list[str]:
        domain = {}
        vvvprint(f"{self.__class__.__name__}: Computing domain of visible variables...")
        for scope in reversed(self.stack):
            domain.update({name: None for name in scope.domain()})

        log_case.set("success", domain=domain)
        return list(domain.keys())



