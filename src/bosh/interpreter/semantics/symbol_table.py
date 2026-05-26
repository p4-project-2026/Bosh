from bosh.interpreter.executor.environment.table import Table
import bosh.helper_functions.type_helper as t_h 
from bosh.helper_functions.type_helper import EMPTY_LIST_TYPE, UNKNOWN_LIST_TYPE
from bosh.helper_functions.logged import logged, LogCase
        
class Symbol_Table(Table[set[str]]):

    @logged(
        start=lambda self, name, type_value: (
            f"Attempting to bind variable '{name}' to type set {type_value} in current scope..."
        ),
        success={
            "bound": lambda self, name, type_value: (
                f"Variable '{name}' bound to type set {type_value} in current scope successfully."
            ),
            "narrowed": lambda self, name, type_value: (
                f"Variable '{name}' narrowed to type set {type_value} in current scope successfully."
            ),
            "compatible": lambda self, name, type_value: (
                f"Variable '{name}' already bound to a compatible type set in current scope. No update needed."
            )
        }
    )
    def bind(self, name: str, type_value: set[str], log_case: LogCase):
        if not type_value:
            raise Exception(f"SymbolTable: Cannot bind variable '{name}' to empty type set.")
    
        if name not in self.table:
  
            self.table[name] = type_value.copy()
            log_case.set("bound")
            return
        current_type = self.table[name]
        if current_type == {"UNKNOWN"} or current_type == {"any"} or current_type == {"null"}:
            self.table[name] = type_value.copy()
            log_case.set("narrowed")
            return # Allow unknown and any to be treated as any other type
    
        if type_value == {"UNKNOWN"} or type_value == {"any"}:
            log_case.set("compatible")
            return # Allow unknown and any to be treated as any other type
        if current_type == type_value:
            log_case.set("compatible")
            return # Allow re-binding to the same type
    
        overlap = current_type & type_value
        if overlap:
            self.table[name] = overlap
            log_case.set("narrowed")
            return
        
    
        if current_type in ({EMPTY_LIST_TYPE}, {UNKNOWN_LIST_TYPE}) and t_h.has_concrete_list_type(type_value):
            self.table[name] = type_value.copy() # Allow list to overwrite list<any> and list<UNKNOWN> with specific list type
            log_case.set("narrowed")
            return
    
    
        if (type_value in ({UNKNOWN_LIST_TYPE}, {EMPTY_LIST_TYPE}) 
        and t_h.has_concrete_list_type(current_type)):
            log_case.set("compatible")
            return # Allow list<any> and list<UNKNOWN> to be treated as specific list type
    
        if type_value == {UNKNOWN_LIST_TYPE} and current_type == {EMPTY_LIST_TYPE}:
            self.table[name] = {UNKNOWN_LIST_TYPE} # Allow list<UNKNOWN> to overwrite as list<any>
            log_case.set("narrowed")
            return
    
        raise Exception(f"Variable '{name}' already bound to a different type in current scope.")


    @logged(
        start=lambda self, name: (
            f"Attempting to look up variable '{name}' in a scope..."
        ),
        success={
            "success": lambda self, name, type_value: (
                f"Variable '{name}' found in current scope with type set {type_value}."
            )
        }
    )
    def lookup(self, name: str, log_case: LogCase) -> set[str]:
       
        if name in self.table:
            value = self.table[name].copy()
            log_case.set("success", type_value=value)
            return value
        raise Exception(f"Variable '{name}' not found in scope.")
    
    