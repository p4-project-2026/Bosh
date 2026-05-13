from .table import Table
from .function_binding import FunctionBinding
from typing import TypeVar, Generic, Type, Dict

T = TypeVar('T')


class ScopeStack(Generic[T]):
    def __init__(self, table_class: Type[Table[T]] = Table):
        self.table_class = table_class
        self.stack: list[Table[T]] = [self.table_class()]  # Start with global scope

    def new_scope(self):
        vvvprint("ScopeStack: Entering new scope...")
        self.stack.append(self.table_class())
        vvvprint("ScopeStack: New scope entered successfully.")

    def exit_scope(self):
        if len(self.stack) == 1:
            raise Exception("Cannot exit global scope.")
            
        if self.stack[-2].function_scope:
            vvvprint("ScopeStack: Exiting function scope...")
            self.stack.pop()  # pop function body scope
            self.stack.pop()  # pop captured function boundary scope
            vvvprint("ScopeStack: Function scope exited successfully.")
            return
        vvvprint("ScopeStack: Exiting current scope...")
        self.stack.pop()
        vvvprint("ScopeStack: Current scope exited successfully.")


    def enter_function_scope(self, function_def: FunctionBinding):
        vvvprint(f"ScopeStack: Entering function scope for function with parameters {function_def.parameters}...")
        function_scope = function_def.captured_scope.copy(function_scope=True)
        self.stack.append(function_scope)
        vvvprint("ScopeStack: Captured function scope from definition entered successfully.")
        self.new_scope()  # Create a new scope for the function body
        vvvprint("ScopeStack: Function body scope entered successfully.")

    def snapshot(self) -> Table[T]:
        visible_scopes: list[Table[T]] = []
        vvvprint("ScopeStack: Creating snapshot of current visible scopes...")
        for scope in reversed(self.stack):
            visible_scopes.append(scope)
            if scope.function_scope:
                break  # Stop at the first function scope
        vvvprint(f"ScopeStack: Snapshot of visible scopes created successfully. Number of scopes in snapshot: {len(visible_scopes)}")

        snapshot: Dict[str, T] = {}
        vvvprint("ScopeStack: Merging visible scopes into snapshot...")
        for scope in reversed(visible_scopes):
            snapshot.update(scope.get_snapshot())
        vvvprint("ScopeStack: Visible scopes merged into snapshot successfully.")
        vvvprint(f"ScopeStack: Snapshot content: {snapshot}")
        snapshot_table= self.table_class(table=snapshot)
        vvvprint("ScopeStack: Snapshot table created successfully.")
        return snapshot_table

    def lookup(self, name: str) -> T:
        vvvprint(f"ScopeStack: Looking up variable '{name}' in visible scopes...")
        for scope in reversed(self.stack):
            if scope.contains(name):
                vvvprint(f"ScopeStack: Variable '{name}' found in scope. Value: {scope.lookup(name)}")
                return scope.lookup(name)
            if scope.function_scope:  # If we reach a function scope or global scope, stop searching
                vvvprint(f"ScopeStack: Reached function scope while looking up variable '{name}'. Stopping search.")
                break
        raise Exception(f"Variable '{name}' not found in scope.")
    
    def lookup_assign(self, name: str) -> T:
        vvvprint(f"ScopeStack: Looking up variable '{name}' for assignment...")
        for scope in reversed(self.stack):
            if scope.function_scope:  # If we reach a function scope or global scope, stop searching
                vvvprint(f"ScopeStack: Reached function scope while looking up variable '{name}' for assignment. Stopping search.")
                break    
            if scope.contains(name):
                vvvprint(f"ScopeStack: Variable '{name}' found in scope for assignment. Value: {scope.lookup(name)}")
                return scope.lookup(name)
        raise Exception(f"Variable '{name}' not found in scope.")

    def bind(self, name: str, value: T):
        vvvprint(f"ScopeStack: Binding variable '{name}' to value {value} in current scope...")
        if self.stack[-1].contains(name):
            raise Exception(f"Variable '{name}' already defined in current scope.")
        vvvprint(f"ScopeStack: Variable '{name}' bound to value {value} in current scope successfully.")
        self.stack[-1].bind(name, value)

    def domain(self) -> list[str]:
        domain = {}
        vvvprint("ScopeStack: Computing domain of visible variables...")
        for scope in reversed(self.stack):
            vvvprint(f"ScopeStack: Adding variables from scope to domain: {scope.domain()}")
            domain.update({name: None for name in scope.domain()})