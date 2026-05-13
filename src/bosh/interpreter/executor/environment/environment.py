from typing import Optional
from .scope_stack import ScopeStack
from .store import Store
from .table import Table
from .function_binding import FunctionBinding
from .var_table import VarTable
from pathlib import Path

class Environment:
    def __init__(self):
        self.v_table = ScopeStack[int](VarTable)
        self.f_table = Table[FunctionBinding]()
        self.store = Store()
        self.CD: str = str(Path.cwd())  # Current Directory, used for resolving file paths in import statements

    def new_scope(self):
        """Create a new variable scope."""
        vvvprint("Entering new scope...")
        self.v_table.new_scope()
        vvvprint("New scope entered.")
    def exit_scope(self):
        vvvprint("Exiting current scope...")
        """Exit the current variable scope."""
        vvvprint("Current scope exited.")
        self.v_table.exit_scope()
    
    def get_function(self, name: str) -> FunctionBinding:
        """Look up a function definition by name."""
        try:
            vvvprint(f"Environment: Looking up function '{name}'...")
            function_def = self.f_table.lookup(name)
            vvvprint(f"Environment: Function '{name}' found: {function_def}")
            return function_def

        except Exception as e:
            raise Exception(f"Environment: Error looking up function '{name}': {e}")

    def enter_function_scope(self,name: str):
        """Enter a new function scope based on the function definition associated with the given name. returns the FunctionBinding for the function being entered."""

        try:
            vvvprint(f"Environment: Entering function scope for function '{name}'...")
            self.v_table.enter_function_scope(function_def = self.f_table.lookup(name))
            vvvprint(f"Environment: Function scope for function '{name}' entered successfully.")
        except Exception as e:
            raise Exception(f"Environment: Error looking up function '{name}': {e}")
        
    def assign_variable(self, name: str, value: any):
        """Assign a value to a variable. If the variable already exists in any assingnable scope, update its value. Otherwise, create a new variable in the current scope."""
        vvvprint(f"Environment: Assigning value to variable '{name}': {value}")
        try:
            vvvprint(f"Environment: Looking up variable '{name}' for assignment...")
            loc = self.v_table.lookup_assign(name)  # Check if variable exists in any visible scope
            vvvprint(f"Environment: Variable '{name}' found at location {loc}. Updating value...")
            self.store.set(loc, value)  # Update the value in the store
            vvvprint(f"Environment: Variable '{name}' updated successfully.")
        except Exception:
            vvvprint(f"Environment: Variable '{name}' not found in visible scopes. Creating new variable...")
            loc = self.store.allocate(value)  # Allocate a new cell in the store
            vvvprint(f"Environment: New variable '{name}' allocated at location {loc} with value {value}. Binding to current scope...")
            self.v_table.bind(name, loc)  # Bind the variable name to the new location in the current scope
            vvvprint(f"Environment: Variable '{name}' bound to location {loc} in current scope successfully.")

    def lookup_variable(self, name: str) -> any:
        """Look up the value of a variable by name. Search through visible scopes and return the value from the store."""
        
        try:
            vvvprint(f"Environment looking up variable '{name}'...")
            loc = self.v_table.lookup(name)  # Get the location of the variable from the scope stack
            vvvprint(f"Variable '{name}' found at location {loc}. Retrieving value from store...")
            value = self.store.get(loc)  # Retrieve the value from the store using the location
            vvvprint(f"Value of variable '{name}' retrieved successfully: {value}")
            return value
        except Exception as e:
            raise Exception(f"Error looking up variable '{name}': {e}")
        
    
    def snapshot(self) -> VarTable:
        """Create a snapshot of the current variable scope stack. This is used for capturing the environment when defining a function."""
        return self.v_table.snapshot()
    
    def bind_function(self, name: str, function_def: FunctionBinding):
        """Bind a function definition to a name in the function table."""
        try:
            self.f_table.bind(name, function_def)
        except Exception as e:
            raise Exception(f"Error binding function '{name}': {e}")
        
    def __lookup_function__(self, name: str) -> FunctionBinding:
        """Look up a function definition by name."""
        try:
            return self.f_table.lookup(name)
        except Exception as e:
            raise Exception(f"Error looking up function '{name}': {e}")

    def get_current_directory(self) -> str:
        """Get the current directory for resolving file paths in import statements."""
        return self.CD
    
    def set_current_directory(self, path: str):
        """Set the current directory for resolving file paths in import statements."""
        self.CD = path