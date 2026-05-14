from bosh.interpreter.executor.environment.scope_stack import ScopeStack
from .symbol_table import symbol_table

class SymbolTableScopeStacker(ScopeStack):
    def __init__(self):
        super().__init__(table_class=symbol_table)

    def bind(self, name: str, type_value: set[str]):
        for scope in reversed(self.stack):
            vvvprint(f"SymbolTableScopeStacker: Attempting to bind variable '{name}' to type '{type_value}' in scope: {scope}")
            if scope.contains(name):
                vvvprint(f"SymbolTableScopeStacker: Variable '{name}' found in scope, attempting to bind to type '{type_value}'...")
                try:
                    vvvprint(f"SymbolTableScopeStacker: Binding variable '{name}' to type '{type_value}' in scope...")
                    scope.bind(name, type_value)
                    vvvprint(f"SymbolTableScopeStacker: Successfully bound variable '{name}' to type '{type_value}' in scope.")
                except Exception as e:
                    raise Exception(f"Error binding variable '{name}': {e}")
                return
            vvvprint(f"SymbolTableScopeStacker: Variable '{name}' not found in scope, moving to next outer scope...")
            if scope.function_scope:  # If we reach a function scope or global scope, stop searching
                vvvprint(f"SymbolTableScopeStacker: Reached function stopping search for variable '{name}'.")
                break
        vvvprint(f"SymbolTableScopeStacker: Variable '{name}' not found in any outer scope, binding to type '{type_value}' in current scope...")
        self.stack[-1].bind(name, type_value)  # Bind in the current scope if not found in any outer scope
    
    def bind_local(self, name: str, type_value: set[str]):
        vvvprint(f"SymbolTableScopeStacker: Binding variable '{name}' to type '{type_value}' in current scope...")
        try:
            vvvprint(f"SymbolTableScopeStacker: Attempting to bind variable '{name}' to type '{type_value}' in current scope...")
            self.stack[-1].bind(name, type_value)
            vvvprint(f"SymbolTableScopeStacker: Successfully bound variable '{name}' to type '{type_value}' in current scope.")
        except Exception as e:
            raise Exception(f"Error binding variable '{name}' in local scope: {e}")
        
    def domain(self) -> list[str]:
        vvvprint(f"SymbolTableScopeStacker: Retrieving domain of all visible scopes...")
        domain = set()
        for scope in reversed(self.stack):
            vvvprint(f"SymbolTableScopeStacker: Checking domain of scope: {scope}")
            domain.update(scope.domain())
        
        vvvprint(f"SymbolTableScopeStacker: Domain of all visible scopes retrieved successfully. Domain: {domain}")
        domain_list = list(domain)
        vvvprint(f"SymbolTableScopeStacker: Domain converted to list successfully. Domain list: {domain_list}")
        return domain_list
    