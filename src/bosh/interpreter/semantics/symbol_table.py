from bosh.interpreter.executor.environment.table import Table


        
class Symbol_Table(Table[set[str]]):

    def bind(self, name: str, type_value: set[str]):
        vvvprint(f"SymbolTable: Attempting to bind variable '{name}' to type '{type_value}' in current scope...")
        if not type_value:
                raise Exception(f"SymbolTable: Cannot bind variable '{name}' to empty type set.")
        
        if name not in self.table:
            vvvprint(f"SymbolTable: Variable '{name}' is not yet bound in current scope, binding to type '{type_value}'...")
            self.table[name] = type_value.copy()
            return
        current_type = self.table[name]
        vvvprint(f"SymbolTable: Variable '{name}' already bound to type '{current_type}' in current scope.")

        if current_type == {"UNKNOWN"} or current_type == {"any"}:

            vvvprint(f"SymbolTable: Variable '{name}' is currently bound to '{current_type}', allowing re-binding to any type '{type_value}'...")
            self.table[name] = type_value.copy()
            return # Allow unknown and any to be treated as any other type
        
        if type_value == {"UNKNOWN"} or type_value == {"any"}:
            vvvprint(f"SymbolTable: Attempting to bind variable '{name}' to type '{type_value}' which is 'UNKNOWN' or 'any', allowing re-binding them to current type '{current_type}'...")
            return # Allow unknown and any to be treated as any other type

        if current_type == type_value:
            vvvprint(f"SymbolTable: Variable '{name}' already bound to the same type '{type_value}', allowing re-binding.")
            return # Allow re-binding to the same type
        
        overlap = current_type & type_value
        if overlap:
            vvvprint(f"SymbolTable: Variable '{name}' has overlapping types '{overlap}' with current type '{current_type}' and new type '{type_value}', allowing re-binding to the overlap.")
            self.table[name] = overlap
            return
            
        is_specific_list_type = any(
        t.startswith("list<") and t.endswith(">")
        for t in type_value
        )

            
        if current_type in ({"list<any>"}, {"list<UNKNOWN>"}) and is_specific_list_type:
            vvvprint(f"SymbolTable: Variable '{name}' is currently bound to 'list<any>' or 'list<UNKNOWN>', allowing re-binding to specific list type '{type_value}'.")
            self.table[name] = type_value.copy() # Allow list<any> or list<UNKNOWN> to be treated as any other list type
            return
        
        is_current_specific_list_type = any(
        t.startswith("list<") and t.endswith(">")
        for t in current_type
        )
        
        if type_value in ({"list<UNKNOWN>"}, {"list<any>"}) and is_current_specific_list_type:
            vvvprint(f"SymbolTable: Attempting to bind 'list<UNKNOWN>' or 'list<any>' to variable '{name}' which is currently bound to specific list type '{current_type}', allowing re-binding.")
            return # Allow list<UNKNOWN> to be treated as any other list type
                 
        raise Exception(f"Variable '{name}' already bound to a different type in current scope.")
    
    def lookup(self, name: str) -> set[str]:
        vvvprint(f"SymbolTable: Looking up variable '{name}' in current scope...")
        if name in self.table:
            vvvprint(f"SymbolTable: Variable '{name}' found in current scope with type '{self.table[name]}'.")
            return self.table[name].copy()
        raise Exception(f"Variable '{name}' not found in scope.")
    
