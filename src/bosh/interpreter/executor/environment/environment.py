from typing import Optional
from .scope_stack import ScopeStack
from .store import Store
from .table import Table
from .function_table import FunctionTable
from .function_binding import FunctionBinding
from .var_table import VarTable
from pathlib import Path
from bosh.helper_functions.logged import logged, LogCase

class Environment:
    def __init__(self):
        self.v_table = ScopeStack[int](VarTable)
        self.f_table = FunctionTable()
        self.store = Store()
        self.CD: str = str(Path.cwd())  # Current Directory, used for resolving file paths in import statements


    @logged(
        start=lambda self: (
            f"Creating a new variable scope..."
        ),
        success={
            "success": lambda self: (
                f"New variable scope created successfully."
            )
        }
    )
    def new_scope(self, log_case: LogCase):
        """Create a new variable scope."""
        self.v_table.new_scope()
        log_case.set("success")


    @logged(
        start=lambda self: (
            f"Attempting to exit current variable scope..."
        ),
        success={
            "success": lambda self: (
                f"Exited current variable scope successfully."
            )
        }
    )
    def exit_scope(self, log_case: LogCase):
        """Exit the current variable scope."""
        self.v_table.exit_scope()
        log_case.set("success")


    @logged(
        start=lambda self, name: (
            f"Attempting to look up function '{name}' in function table..."
        ),
        success={
            "success": lambda self, name, function_def: (
                f"Function '{name}' found in function table with definition: \n{function_def}\n"
            )
        }
    )
    def get_function(self, name: str, log_case: LogCase) -> FunctionBinding:
        """Look up a function definition by name."""
        try:
            function_def = self.f_table.lookup(name)

            log_case.set("success", function_def=function_def)
            return function_def

        except Exception as e:
            raise Exception(f"Environment: Error looking up function '{name}': {e}")


    @logged(
        start=lambda self, name: (
            f"Attempting to enter function scope for function '{name}'..."
        ),
        success={
            "success": lambda self, name, function_def: (
                f"Function scope for function '{name}' entered successfully based on function definition: \n{function_def}\n"
            )
        }
    )
    def enter_function_scope(self,name: str, log_case: LogCase):
        """Enter a new function scope based on the function definition associated with the given name. returns the FunctionBinding for the function being entered."""

        try:
            function_def = self.f_table.lookup(name)
            self.v_table.enter_function_scope(function_def=function_def)
            log_case.set("success", function_def=function_def)
        except Exception as e:
            raise Exception(f"Environment: Error looking up function '{name}': {e}")


    @logged(
        start=lambda self, name, value: (
            f"Attempting to assign value to variable '{name}': {value}"
        ),
        success={
            "updated": lambda self, name, value: (
                f"Variable '{name}' updated to value {value} successfully in existing scope."
            ),
            "logged": lambda self, name, value: (
                f"New variable '{name}' assigned value {value} successfully in current scope."
            )
        }
    )
    def assign_variable(self, name: str, value: any, log_case: LogCase):
        """Assign a value to a variable. If the variable already exists in any assingnable scope, update its value. Otherwise, create a new variable in the current scope."""
        try:
            loc = self.v_table.lookup_assign(name)  # Check if variable exists in any visible scope
            self.store.set(loc, value)  # Update the value in the store
            log_case.set("updated")
        except Exception:
            loc = self.store.allocate(value)  # Allocate a new cell in the store
            self.v_table.bind(name, loc)  # Bind the variable name to the new location in the current scope
            log_case.set("logged")


    @logged(
        start=lambda self, name, value: (
            f"Attempting to bind local variable '{name}' in current scope..."
        ),
        success={
            "success": lambda self, name, value: (
                f"Local variable '{name}' bound to value {value} in current scope successfully."
            )
        }
    )
    def bind_local_variable(self, name: str, value: any, log_case: LogCase):
        """Bind a variable to the current scope without checking outer scopes. This is used for binding function parameters and local variables."""
        loc = self.store.allocate(value)  # Allocate a new cell in the store
        self.v_table.bind(name, loc)  # Bind the variable name to the new location in the current scope
        log_case.set("success")


    @logged(
        start=lambda self, name: (
            f"Attempting to look up variable '{name}' in environment..."
        ),
        success={
            "success": lambda self, name, value: (
                f"Variable '{name}' found in environment with value {value}."
            )
        }
    )
    def lookup_variable(self, name: str, log_case: LogCase) -> any:
        """Look up the value of a variable by name. Search through visible scopes and return the value from the store."""        
        try:
            loc = self.v_table.lookup(name)  # Get the location of the variable from the scope stack
            value = self.store.get(loc)  # Retrieve the value from the store using the location
            log_case.set("success", value=value)
            return value
        except Exception as e:
            raise Exception(f"Error looking up variable '{name}': {e}")


    @logged(
        start=lambda self: (
            f"Attempting to create snapshot of current variable scope stack..."
        ),
        success={
            "success": lambda self, snapshot: (
                f"Snapshot of current variable scope stack created successfully:\n{snapshot}\n"
            )
        }
    )
    def snapshot(self, log_case: LogCase) -> VarTable:
        """Create a snapshot of the current variable scope stack. This is used for capturing the environment when defining a function."""
        snapshot = self.v_table.snapshot()
        log_case.set("success", snapshot=snapshot)
        return snapshot


    @logged(
        start=lambda self, name, function_def: (
            f"Attempting to bind function '{name}' to function definition {function_def} in function table..."
        ),
        success={
            "success": lambda self, name, function_def: (
                f"Function '{name}' bound to function definition {function_def} in function table successfully."
            )
        }
    )
    def bind_function(self, name: str, function_def: FunctionBinding, log_case: LogCase):
        """Bind a function definition to a name in the function table."""
        try:
            self.f_table.bind(name, function_def)
            log_case.set("success")
        except Exception as e:
            raise Exception(f"Error binding function '{name}': {e}")


    @logged(
        start=lambda self: (
            f"Attempting to get current directory for environment..."
        ),
        success={
            "success": lambda self, CD: (
                f"Current directory for environment retrieved successfully: {CD}"
            )
        }
    )
    def get_current_directory(self, log_case: LogCase) -> str:
        """Get the current directory for resolving file paths in import statements."""
        cd = self.CD
        log_case.set("success", CD=cd)
        return cd

   
    @logged(
        start=lambda self, path: (
            f"Attempting to set current directory for environment to: {path}"
        ),
        success={
            "success": lambda self, path: (
                f"Current directory for environment set successfully to: {path}"
            )
        }
    )
    def set_current_directory(self, path: str, log_case: LogCase):
        """Set the current directory for resolving file paths in import statements."""
        self.CD = path
        log_case.set("success", path=self.CD)