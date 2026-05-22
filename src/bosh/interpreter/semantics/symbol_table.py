from bosh.interpreter.executor.environment.table import Table
import bosh.helper_functions.type_helper as t_h 
from bosh.helper_functions.type_helper import EMPTY_LIST_TYPE, UNKNOWN_LIST_TYPE
        
class Symbol_Table(Table[set[str]]):

    def bind(self, name: str, type_value: set[str]):
        if not type_value:
            raise Exception(f"SymbolTable: Cannot bind variable '{name}' to empty type set.")
    
        if name not in self.table:
  
            self.table[name] = type_value.copy()
            return
        current_type = self.table[name]
        if current_type == {"UNKNOWN"} or current_type == {"any"} or current_type == {"null"}:
            self.table[name] = type_value.copy()
            return # Allow unknown and any to be treated as any other type
    
        if type_value == {"UNKNOWN"} or type_value == {"any"}:
            return # Allow unknown and any to be treated as any other type
        if current_type == type_value:
            return # Allow re-binding to the same type
    
        overlap = current_type & type_value
        if overlap:
            self.table[name] = overlap
            return
        
    
        if current_type in ({EMPTY_LIST_TYPE}, {UNKNOWN_LIST_TYPE}) and t_h.has_concrete_list_type(type_value):
            self.table[name] = type_value.copy() # Allow list to overwrite list<any> and list<UNKNOWN> with specific list type
            return
    
    
        if (type_value in ({UNKNOWN_LIST_TYPE}, {EMPTY_LIST_TYPE}) 
        and t_h.has_concrete_list_type(current_type)):
            return # Allow list<any> and list<UNKNOWN> to be treated as specific list type
    
        if type_value == {UNKNOWN_LIST_TYPE} and current_type == {EMPTY_LIST_TYPE}:
            self.table[name] = {UNKNOWN_LIST_TYPE} # Allow list<UNKNOWN> to overwrite as list<any>
            return
    
        raise Exception(f"Variable '{name}' already bound to a different type in current scope.")
    
    def lookup(self, name: str) -> set[str]:
       
        if name in self.table:
            return self.table[name].copy()
        raise Exception(f"Variable '{name}' not found in scope.")
    
    