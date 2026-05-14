from bosh.interpreter.executor.environment.table import Table

        
class symbol_table(Table[set[str]]):

    def bind(self, name: str, type_value: set[str]):
        vvvprint(f"SymbolTable: Attempting to bind variable '{name}' to type '{type_value}' in current scope...")
        if name in self.table:
            
                
            vvvprint(f"SymbolTable: Variable '{name}' already bound to type '{self.table[name]}' in current scope.")
            if self.table[name] == type_value:
                vvvprint(f"SymbolTable: Variable '{name}' already bound to the same type '{type_value}', allowing re-binding.")
                return # Allow re-binding to the same type
            if self.table[name].issubset(type_value) or type_value.issubset(self.table[name]):
                vvvprint(f"SymbolTable: Variable '{name}' already bound to a compatible type '{self.table[name]}', allowing re-binding to type '{type_value}'.")
                self.table[name] = self.table[name].union(type_value) # Allow re-binding to a compatible type by taking the union of the types
                return
            if "number" in self.table[name] or "decimal" in self.table[name]:
                if "number" in type_value or "decimal" in type_value:
                    vvvprint(f"SymbolTable: Variable '{name}' already bound to a numeric type '{self.table[name]}', allowing re-binding to compatible numeric type '{type_value}'.")
                    self.table[name] = type_value # Allow number and decimal to be treated as compatible types
                    return
            if self.table[name] == {"any"}:
                vvvprint(f"SymbolTable: Variable '{name}' is currently bound to 'any', allowing re-binding to any type '{type_value}'.")
                self.table[name] = type_value
                return # Allow any to be treated as any other type
            # if self.table[name] == list<any> and has list<something>
            if self.table[name] == {"list<any>"} and (any(t.startswith("list<") and t.endswith(">") for t in type_value) or not any(t.startswith("list<") and t.endswith(">") for t in type_value)):
                vvvprint(f"SymbolTable: Variable '{name}' is currently bound to 'list<any>', allowing re-binding to compatible list type '{type_value}'...")
                self.table[name] = type_value # Allow list<any> to be treated as any other list type
                return
            if self.table[name] == {"UNKNOWN"}:
                vvvprint(f"SymbolTable: Variable '{name}' is currently bound to 'UNKNOWN', allowing re-binding to any type '{type_value}'.")
                self.table[name] = type_value
                return # Allow unknown to be treated as any other type

            vvvprint(f"SymbolTable: Variable '{name}' already bound to a different type '{self.table[name]}', checking for compatible types...")
            match self.table[name][0]:
                
                case "any":
                    vvvprint(f"SymbolTable: Variable '{name}' is currently bound to 'any', allowing re-binding to any type.")
                    self.table[name][0] = type_value
                    return # Allow any to be treated as any other type
                case "list<any>":
                    vvvprint(f"SymbolTable: Variable '{name}' is currently bound to 'list<any>', checking if new type '{type_value}' is compatible...") 
                    if type_value.startswith("list<") or not type_value.endswith(">"):
                    
                        self.table[name][0] = type_value
                        return # Allow list<any> to be treated as any other list type
                case _:
                    vvvprint(f"SymbolTable: Variable '{name}' is currently bound to an incompatible type '{self.table[name]}', raising exception.")

            raise Exception(f"Variable '{name}' already bound to a different type in current scope.")
        vvvprint(f"SymbolTable:  variable '{name}' is not yet bound in current scope, binding to type '{type_value}'...")
        self.table[name] = type_value
    
    def lookup(self, name: str) -> set[str]:
        vvvprint(f"SymbolTable: Looking up variable '{name}' in current scope...")
        if name in self.table:
            vvvprint(f"SymbolTable: Variable '{name}' found in current scope with type '{self.table[name]}'.")
            return self.table[name]
        raise Exception(f"Variable '{name}' not found in scope.")
    
