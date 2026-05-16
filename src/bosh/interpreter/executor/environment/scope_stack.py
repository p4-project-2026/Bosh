from .table import Table
from .function_binding import FunctionBinding
from typing import TypeVar, Generic, Type, Dict

T = TypeVar('T')


class ScopeStack(Generic[T]):
    def __init__(self, table_class: Type[Table[T]] = Table):
        self.table_class = table_class
        self.stack: list[Table[T]] = [self.table_class()]  # Start with global scope

    def new_scope(self):
        vvvprint(f"{self.__class__.__name__}: Entering new scope...")
        self.stack.append(self.table_class())
        vvvprint(f"{self.__class__.__name__}: New scope entered successfully.")

    def exit_scope(self):
        if len(self.stack) == 1:
            raise Exception("Cannot exit global scope.")
            
        if self.stack[-2].function_scope:
            vvvprint(f"{self.__class__.__name__}: Exiting function scope...")
            self.stack.pop()  # pop function body scope
            self.stack.pop()  # pop captured function boundary scope
            vvvprint(f"{self.__class__.__name__}: Function scope exited successfully.")
            return
        vvvprint(f"{self.__class__.__name__}: Exiting current scope...")
        self.stack.pop()
        vvvprint(f"{self.__class__.__name__}: Current scope exited successfully.")


    def enter_function_scope(self, function_def: FunctionBinding):
        vvvprint(f"{self.__class__.__name__}: Entering function scope for function with parameters {function_def.parameters}...")
        function_scope = function_def.captured_scope.copy(function_scope=True)
        self.stack.append(function_scope)
        vvvprint(f"{self.__class__.__name__}: Captured function scope from definition entered successfully.")
        self.new_scope()  # Create a new scope for the function body
        vvvprint(f"{self.__class__.__name__}: Function body scope entered successfully.")

    def snapshot(self) -> Table[T]:
        visible_scopes: list[Table[T]] = []
        vvvprint(f"{self.__class__.__name__}: Creating snapshot of current visible scopes...")
        for scope in reversed(self.stack):
            visible_scopes.append(scope)
            if scope.function_scope:
                break  # Stop at the first function scope
        vvvprint(f"{self.__class__.__name__}: Snapshot of visible scopes created successfully. Number of scopes in snapshot: {len(visible_scopes)}")

        snapshot: Dict[str, T] = {}
        vvvprint(f"{self.__class__.__name__}: Merging visible scopes into snapshot...")
        for scope in reversed(visible_scopes):
            snapshot.update(scope.get_snapshot())
        vvvprint(f"{self.__class__.__name__}: Visible scopes merged into snapshot successfully.")
        vvvprint(f"{self.__class__.__name__}: Snapshot content: {snapshot}")
        snapshot_table= self.table_class(table=snapshot)
        vvvprint(f"{self.__class__.__name__}: Snapshot table created successfully.")
        return snapshot_table

    def lookup(self, name: str) -> T:
        vvvprint(f"{self.__class__.__name__}: Looking up variable '{name}' in visible scopes...")
        for scope in reversed(self.stack):
            if scope.contains(name):
                vvvprint(f"{self.__class__.__name__}: Variable '{name}' found in scope. Value: {scope.lookup(name)}")
                return scope.lookup(name)
            if scope.function_scope:  # If we reach a function scope or global scope, stop searching
                vvvprint(f"{self.__class__.__name__}: Reached function scope while looking up variable '{name}'. Stopping search.")
                break
        raise Exception(f"Undefined variable '{name}'")
    
    def lookup_assign(self, name: str) -> T:
        vvvprint(f"{self.__class__.__name__}: Looking up variable '{name}' for assignment...")
        for scope in reversed(self.stack):
            if scope.function_scope:  # If we reach a function scope or global scope, stop searching
                vvvprint(f"{self.__class__.__name__}: Reached function scope while looking up variable '{name}' for assignment. Stopping search.")
                break    
            if scope.contains(name):
                vvvprint(f"{self.__class__.__name__}: Variable '{name}' found in scope for assignment. Value: {scope.lookup(name)}")
                return scope.lookup(name)
        raise Exception(f"Variable '{name}' not found in scope.")
    
    def contains(self, name: str) -> bool:
        for scope in reversed(self.stack):
            if scope.contains(name):
                return True
            if scope.function_scope:  # If we reach a function scope or global scope, stop searching
                break
        return False

    def bind(self, name: str, value: T):
        vvvprint(f"{self.__class__.__name__}: Binding variable '{name}' to value {value} in current scope...")
        if self.stack[-1].contains(name):
            raise Exception(f"Variable '{name}' already defined in current scope.")
        vvvprint(f"{self.__class__.__name__}: Variable '{name}' bound to value {value} in current scope successfully.")
        self.stack[-1].bind(name, value)

    def domain(self) -> list[str]:
        domain = {}
        vvvprint(f"{self.__class__.__name__}: Computing domain of visible variables...")
        for scope in reversed(self.stack):
            vvvprint(f"{self.__class__.__name__}: Adding variables from scope to domain: {scope.domain()}")
            domain.update({name: None for name in scope.domain()})