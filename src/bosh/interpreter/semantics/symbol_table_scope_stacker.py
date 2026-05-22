from bosh.interpreter.executor.environment.scope_stack import ScopeStack
from .symbol_table import Symbol_Table
from bosh.helper_functions.logged import logged, LogCase

class SymbolTableScopeStacker(ScopeStack):
    def __init__(self):
        super().__init__(table_class=Symbol_Table)


    @logged(
        start=lambda self, name, type_value: (
            f"Attempting to bind variable '{name}' to type '{type_value}' in current scope stack..."
        ),
        success={
            "compatible": lambda self, name, type_value: (
                f"Variable '{name}' already bound to a compatible type in an outer scope."
            ),
            "Bound": lambda self, name, type_value: (
                f"Variable '{name}' bound to type '{type_value}' in current scope stack successfully."
            )
        }
    )
    def bind(self, name: str, type_value: set[str], log_case: LogCase):
        for scope in reversed(self.stack):
            if scope.contains(name):
                try:
                    scope.bind(name, type_value)
                    log_case.set("compatible")
                except Exception as e:
                    raise Exception(f"Error binding variable '{name}': {e}")
                return
            if scope.function_scope:  # If we reach a function scope or global scope, stop searching
                break
        self.stack[-1].bind(name, type_value)  # Bind in the current scope if not found in any outer scope
        log_case.set("Bound")


    @logged(
        start=lambda self, name, type_value: (
            f"Attempting to bind local variable '{name}' to type '{type_value}' in current scope..."
        ),
        success={
            "success": lambda self, name, type_value: (
                f"Local variable '{name}' bound to type '{type_value}' in current scope successfully."
            )
        }
    )
    def bind_local(self, name: str, type_value: set[str], log_case: LogCase):
        try:
            self.stack[-1].bind(name, type_value)
            log_case.set("success")

        except Exception as e:
            raise Exception(f"Error binding variable '{name}' in local scope: {e}")


    @logged(
        start=lambda self: (
            f"Retrieving domain of all visible scopes in current scope stack..."
        ),
        success={
            "success": lambda self, domain: (
                f"Domain of all visible scopes in current scope stack retrieved successfully: \n{domain}\n"
            )
        }
    )
    def domain(self, log_case: LogCase) -> list[str]:
        domain = set()
        for scope in reversed(self.stack):
            domain.update(scope.domain())
        
        domain_list = list(domain)
        log_case.set("success", domain=domain_list)
        return domain_list
    

    def snapshot(self) -> Symbol_Table:
        return super().snapshot()


    @logged(
        start=lambda self, snapshot: (
            f"Attempting to update snapshot of current scope stack with visible variables..."
        ),
        success={
            "success": lambda self, snapshot: (
                f"Snapshot of current scope stack updated successfully with visible variables. Snapshot domain: \n{snapshot.domain()}\n"
            )
        }
    )
    def update_snapshot(self, snapshot: Symbol_Table, log_case: LogCase):
        try:
            domain = snapshot.domain()

            for name in domain:
                if self.contains(name):
                    snapshot.bind(name, self.lookup(name))

            log_case.set("success", snapshot=snapshot)
        except Exception as e:
            raise Exception(f"Error updating snapshot: {e}")


    @logged(
        start=lambda self, function_scope: (
            f"Attempting to enter new function scope with snapshot of captured variables..."
        ),
        success={
            "success": lambda self, function_scope: (
                f"Function scope entered successfully with snapshot of captured variables."
            )
        }
    )
    def enter_function_scope(self, function_scope: Symbol_Table, log_case: LogCase):
        in_function_scope = function_scope.copy()
        in_function_scope.function_scope = True
        self.stack.append(in_function_scope)
        self.new_scope()  # Create a new scope for the function body
        log_case.set("success")

        