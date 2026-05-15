from .ast_base import *

@dataclass
class Print(ASTNode):
    expression: ASTNode

    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        try:
            self.expression.check(v_table, f_table)
        except Exception as e:
            raise TraceError(node = self, cause = e, hide_trace = True)

    def execute(self, env: Environment) -> None:
        try:
            value = self.expression.execute(env)
            value = value if type(value) != bool else ("true" if value else "false")
            print(value)
        except Exception as e:
            raise TraceError(node = self, cause = e, hide_trace = True)


@dataclass
class IfElse(ASTNode):
    condition: ASTNode
    then_branch: Block
    else_branch: Optional[Block]
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        try:
            condition_type = self.condition.check(v_table, f_table)
            if condition_type != "boolean":
                raise TraceError(node = self, cause = f"Condition in if statement must be of type 'boolean', got '{condition_type}'")
            v_table.new_scope()
            self.then_branch.check(v_table, f_table)
            v_table.exit_scope()            
            if self.else_branch:
                v_table.new_scope()
                self.else_branch.check(v_table, f_table)
                v_table.exit_scope()
        except Exception as e:
            raise TraceError(node = self, cause = e, hide_trace = True)

    def execute(self, env: Environment) -> None:
        try:
            condition_value = self.condition.execute(env)
            value = None
            if condition_value:
                env.new_scope()
                value = self.then_branch.execute(env)
                env.exit_scope()
            elif self.else_branch:
                env.new_scope()
                value = self.else_branch.execute(env)
                env.exit_scope()
            return value
        except Exception as e:
            raise TraceError(node = self, cause = e, hide_trace = True)


@dataclass
class Fallback(ASTNode):
    primary_stmt: ASTNode
    fallback_stmt: ASTNode
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        try:
            self.primary_stmt.check(v_table, f_table)
            self.fallback_stmt.check(v_table, f_table)
        except Exception as e:
            raise TraceError(node = self, cause = e)

    def execute(self, env: Environment) -> None:
        try:
            self.primary_stmt.execute(env)
        except Exception:
            try:
                self.fallback_stmt.execute(env)
            except Exception as e:
                raise TraceError(node = self, cause = e)

@dataclass
class ForAll(ASTNode):
    iterator_name: str
    iterable: ASTNode
    body: Block
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        try:
            iterable_type = self.iterable.check(v_table, f_table)
            if iterable_type is None:
                return
            if iterable_type != "text" and not (iterable_type.startswith("list<") and iterable_type.endswith(">")):
                raise TraceError(node = self, cause = f"Iterable in for all statement must be of type 'list' or 'text', got '{iterable_type}'")
            element_type = iterable_type[5:-1] if iterable_type.startswith("list<") else "text"
            v_table.new_scope()
            v_table.bind(self.iterator_name, element_type)
            self.body.check(v_table, f_table)
            v_table.exit_scope()
        except Exception as e:
            raise TraceError(node = self, cause = e, hide_trace = True)
        
    def execute(self, env: Environment) -> None:
        try:
            value = None
            iterable_value = self.iterable.execute(env)
            if iterable_value is None:
                return
            if isinstance(iterable_value, str):
                iterable_value = [iterable_value]
            
            for item in iterable_value:
                env.new_scope()
                try:
                    env.assign_variable(self.iterator_name, item)
                    value = self.body.execute(env)
                    if value is not None:
                        break
                finally:
                    env.exit_scope()
            return value
        except Exception as e:
            raise TraceError(node = self, cause = e, hide_trace = True)

@dataclass
class RepeatUntil(ASTNode):
    condition: ASTNode
    body: Block
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        try:        
            condition_type = self.condition.check(v_table, f_table)
            if condition_type != "boolean":
                raise TraceError(node = self, cause = f"Condition in repeat until statement must be of type 'boolean', got '{condition_type}'")
            self.body.check(v_table, f_table)
        except Exception as e:
            raise TraceError(node = self, cause = e)

    def execute(self, env: Environment) -> None:
        try:
            value = None
            env.new_scope()
            while True:
                value = self.body.execute(env)
                if value is not None:
                    break
                condition_value = self.condition.execute(env)
                if condition_value:
                    break
            env.exit_scope()
            return value
        except Exception as e:
            raise TraceError(node = self, cause = e)
        
@dataclass
class Count(ASTNode):
    iterator_name: Optional[str]
    from_: ASTNode
    to_: ASTNode
    body: Block
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        try:
            from_type = self.from_.check(v_table, f_table)
            to_type = self.to_.check(v_table, f_table)
            if from_type != "number" or to_type != "number":
                raise TraceError(node = self, cause = f"'from' and 'to' expressions in count statement must be of type 'number', got '{from_type}' and '{to_type}'")
            
            v_table.new_scope()
            if self.iterator_name:
                v_table.bind(self.iterator_name, "number")
            self.body.check(v_table, f_table)
            v_table.exit_scope()
        except Exception as e:
            raise TraceError(node = self, cause = e)

    def execute(self, env: Environment) -> None:
        try:
            value = None
            from_value = self.from_.execute(env)
            to_value = self.to_.execute(env)
            for i in range(from_value, to_value + 1):
                env.new_scope()
                if self.iterator_name:
                    try:
                        env.assign_variable(self.iterator_name, i)
                        value = self.body.execute(env)
                        if value is not None:
                            break
                    finally:
                        env.exit_scope()
                else:
                    try:
                        value = self.body.execute(env)
                        if value is not None:
                            break
                    finally:
                        env.exit_scope()
            return value
        except Exception as e:
            raise TraceError(node = self, cause = e)

@dataclass
class Quit(ASTNode):
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        return
    
    def execute(self, env: Environment) -> None:
        raise SystemExit()


@dataclass
class ListAdd(ASTNode):
    target: ASTNode
    item: ASTNode
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        try:
            target_type = self.target.check(v_table, f_table)
            self.item.check(v_table, f_table)

            if not target_type.startswith("list<") or not target_type.endswith(">"):
                raise TraceError(node = self, cause = f"Cannot add to type '{target_type}'. Can only add to lists.")
            
            if target_type == "list<any>":
                item_type = self.item.check(v_table, f_table)
                v_table.bind(self.target.name, f"list<{item_type}>")
        except Exception as e:
            raise TraceError(node = self, cause = e)

    def execute(self, env: Environment) -> None:
        try:
            target_value = self.target.execute(env)
            item_value = self.item.execute(env)
            target_value.append(item_value)
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class ListRemove(ASTNode):
    target: ASTNode
    item: ASTNode
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[str]:
        try:
            target_type = self.target.check(v_table, f_table)
            self.item.check(v_table, f_table)
            if not target_type.startswith("list<") or not target_type.endswith(">"):
                raise TraceError(node = self, cause = f"Cannot remove from type '{target_type}'. Can only remove from lists.")
        except Exception as e:
            raise TraceError(node = self, cause = e)
        
    def execute(self, env: Environment) -> None:
        try:
            target_value = self.target.execute(env)
            item_value = self.item.execute(env)
            try:
                target_value.remove(item_value)
            except ValueError:
                raise TraceError(node = self, cause = f"Item '{item_value}' not found in list.")
        except Exception as e:
            raise TraceError(node = self, cause = e)
            
        
@dataclass
class ListRemoveAt(ASTNode):
    target: ASTNode
    index: ASTNode
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[str]:
        try:
            target_type = self.target.check(v_table, f_table)
            index_type = self.index.check(v_table, f_table)
            if not target_type.startswith("list<") or not target_type.endswith(">"):
                raise TraceError(node = self, cause = f"Cannot remove from type '{target_type}'. Can only remove from lists.")
            if index_type != "int":
                raise TraceError(node = self, cause = f"Index in list remove at statement must be of type 'int', got '{index_type}'")
        except Exception as e:
            raise TraceError(node = self, cause = e)

    def execute(self, env: Environment) -> None:
        try:
            target_value = self.target.execute(env)
            index_value = self.index.execute(env)
            try:
                del target_value[index_value]
            except IndexError:
                raise TraceError(node = self, cause = f"Index '{index_value}' out of range for list.")
        except Exception as e:
            raise TraceError(node = self, cause = e)

@dataclass
class Return(ASTNode):
    expression: ASTNode
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[str]:
        try:
            return self.expression.check(v_table, f_table)
        except Exception as e:
            raise TraceError(node = self, cause = e)

    def execute(self, env: Environment) -> Any:
        try:
            value = self.expression.execute(env)
            return value
        except Exception as e:
            raise TraceError(node = self, cause = e)