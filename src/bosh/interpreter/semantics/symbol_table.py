from bosh.interpreter.executor.environment.table import Table

class symbol_table(Table[str]):

    def bind(self, name: str, type_value: str):
        vvvprint(f"SymbolTable: Attempting to bind variable '{name}' to type '{type_value}' in current scope...")
        if name in self.table:
            vvvprint(f"SymbolTable: Variable '{name}' already bound to type '{self.table[name]}' in current scope.")
            if self.table[name] == type_value:
                vvvprint(f"SymbolTable: Variable '{name}' already bound to the same type '{type_value}', allowing re-binding.")
                return # Allow re-binding to the same type
            vvvprint(f"SymbolTable: Variable '{name}' already bound to a different type '{self.table[name]}', checking for compatible types...")
            match self.table[name]:
                case "number":
                    vvvprint(f"SymbolTable: Variable '{name}' is currently bound to 'number', checking if new type '{type_value}' is compatible...")
                    if type_value is "decimal":
                        vvvprint(f"SymbolTable: Variable '{name}' can be treated as 'number' since new type '{type_value}' is 'decimal', allowing re-binding.")
                        self.table[name] = type_value
                        return # Allow number to be treated as decimal
                case "decimal":
                    vvvprint(f"SymbolTable: Variable '{name}' is currently bound to 'decimal', checking if new type '{type_value}' is compatible...")   
                    if type_value is "number":
                        vvvprint(f"SymbolTable: Variable '{name}' can be treated as 'decimal' since new type '{type_value}' is 'number', allowing re-binding.")
                        self.table[name] = type_value
                        return # Allow decimal to be treated as number
                case "any":
                    vvvprint(f"SymbolTable: Variable '{name}' is currently bound to 'any', allowing re-binding to any type.")
                    self.table[name] = type_value
                    return # Allow any to be treated as any other type
                case "list<any>":
                    vvvprint(f"SymbolTable: Variable '{name}' is currently bound to 'list<any>', checking if new type '{type_value}' is compatible...") 
                    if type_value.startswith("list<") or not type_value.endswith(">"):
                        vvvprint(f"SymbolTable: Variable '{name}' can be treated as 'list<any>' since new type '{type_value}' is a list type, allowing re-binding.")
                        self.table[name] = type_value
                        return # Allow list<any> to be treated as any other list type
                case _:
                    vvvprint(f"SymbolTable: Variable '{name}' is currently bound to an incompatible type '{self.table[name]}', raising exception.")

            raise Exception(f"Variable '{name}' already bound to a different type in current scope.")
        vvvprint(f"SymbolTable:  variable '{name}' is not yet bound in current scope, binding to type '{type_value}'...")
        self.table[name] = type_value
    
    def lookup(self, name: str) -> str:
        if name in self.table:
            return self.table[name]
        raise Exception(f"Variable '{name}' not found in scope.")
    
