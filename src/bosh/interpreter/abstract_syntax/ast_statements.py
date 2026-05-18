from .ast_base import *

@dataclass
class Print(ASTNode):
    expression: ASTNode
    def __post_init__(self):
        super().__init__()

    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        try:
            self.child_return_types.clear()
            vvvprint("Print: Checking print statement...")

            expression_type = self.expression.check(v_table, f_table, inference_context)

            vvvprint(f"Print: Expression type is '{expression_type}'.")
            self.child_return_types["expression"] = (expression_type.copy(), self.expression)
        except Exception as e:
            raise TraceError(node = self, cause = e, hide_trace = True)

    def execute(self, env: Environment) -> None:
        try:
            value = self.expression.execute(env)
            value = value if type(value) != bool else ("true" if value else "false")
            print(value)
        except Exception as e:
            raise TraceError(node = self, cause = e, hide_trace = True)

    def inference(
                v_table: ScopeStack,
                f_table: FuncTable,
                inference_context: InferenceContext,
                old_inference_value: set[str],
                new_inference_value: set[str]) -> None:
        raise Exception("Print does not return a value and cannot be used in inference.")

@dataclass
class IfElse(ASTNode):
    condition: ASTNode
    then_branch: Block
    else_branch: Optional[Block]
    def __post_init__(self):
        super().__init__()     
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        try:
            self.child_return_types.clear()
            vvvprint("IfElse: Checking if-else statement...")
            condition_type = self.condition.check(
                v_table=v_table, 
                f_table=f_table, 
                inference_context=inference_context
            )
            
            valid_condition_types = {"boolean"}
            if condition_type != valid_condition_types:
                if not t_h.is_compatible(condition_type, valid_condition_types):
                    raise Exception(f"Condition in if statement must be of type 'boolean', got '{condition_type}'")
                
                self.condition.inference(
                    v_table=v_table,
                    f_table=f_table,
                    inference_context=inference_context,
                    old_inference_value=condition_type.copy(),
                    new_inference_value=valid_condition_types.copy()
                )
                
                condition_type = valid_condition_types

            self.child_return_types["condition"] = (condition_type.copy(), self.condition)
            saved_inference_state = inference_context.save_state()
            v_table.new_scope()
            while True:
                inference_context.reset()
                self.then_branch.check(
                    v_table=v_table, 
                    f_table=f_table, 
                    inference_context=inference_context
                )

                if not inference_context.has_changed():
                    break

            v_table.exit_scope()
            if self.else_branch:
                v_table.new_scope()
                while True:
                    inference_context.reset()
                    self.else_branch.check(
                        v_table=v_table, 
                        f_table=f_table, 
                        inference_context=inference_context
                    )

                    if not inference_context.has_changed():
                        break

                v_table.exit_scope()

            inference_context.load_state(saved_inference_state)
            vvvprint("IfElse: If-else statement check successful.")
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
        
    def inference(
                v_table: ScopeStack,
                f_table: FuncTable,
                inference_context: InferenceContext,
                old_inference_value: set[str],
                new_inference_value: set[str]) -> None:
        raise Exception("IfElse does not return a value and cannot be used in inference.")


@dataclass
class Fallback(ASTNode):
    primary_stmt: ASTNode
    fallback_stmt: ASTNode
    def __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        try:
            self.child_return_types.clear()
            vvvprint("Fallback: Checking fallback statement...")
            self.primary_stmt.check(v_table=v_table, f_table=f_table, inference_context=inference_context)
            self.fallback_stmt.check(v_table=v_table, f_table=f_table, inference_context=inference_context)
            vvvprint("Fallback: Fallback statement check successful.")
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
            
    def inference(
                v_table: ScopeStack,
                f_table: FuncTable,
                inference_context: InferenceContext,
                old_inference_value: set[str],
                new_inference_value: set[str]) -> None:
        raise Exception("Fallback does not return a value and cannot be used in inference.")

@dataclass
class ForAll(ASTNode):
    iterator_name: str
    iterable: ASTNode
    body: Block
    def __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        try:
            self.child_return_types.clear()
            vvvprint("ForAll: Checking for all statement...")

            iterable_type = self.iterable.check(v_table=v_table,
                                                f_table=f_table, 
                                                inference_context=inference_context
                                                )
            if iterable_type is None:
                raise Exception(f"Iterable in for all statement cannot be of type 'None'", self)

            valid_iterable_type = t_h.get_all_list_types(iterable_type)

            if t_h.contains(iterable_type, "text"):
                valid_iterable_type.add("text")

            if not valid_iterable_type:
                raise Exception(f"Iterable in for all statement must be a list or text type, got '{iterable_type}'")

            if valid_iterable_type != iterable_type:
                self.iterable.inference(
                    v_table=v_table,
                    f_table=f_table,
                    inference_context=inference_context,
                    old_inference_value=iterable_type.copy(),
                    new_inference_value=valid_iterable_type.copy(),
                )
                
                iterable_type = valid_iterable_type

            self.child_return_types["iterable"] = (iterable_type.copy(), self.iterable)

            element_type = t_h.get_list_element_types(iterable_type)
            if t_h.contains(iterable_type, "text"):
                element_type.add("text")
            
            saved_inference_state = inference_context.save_state() 
            v_table.new_scope()
            v_table.bind(self.iterator_name, element_type)
            while True:
                inference_context.reset()
                self.body.check(
                    v_table=v_table,
                    f_table=f_table,
                    inference_context=inference_context
                )
                
                if not inference_context.has_changed():
                    break
            returned_element_type = v_table.lookup(self.iterator_name)
            v_table.exit_scope()
            inference_context.load_state(saved_inference_state)
            if returned_element_type != element_type:
                new_iterable_type = set()
                possible_list_types = set()
                if t_h.has_list_type(iterable_type):
                    possible_list_types.update(t_h.make_set_list_types(returned_element_type))

                # Only keep list types that were possible from the original iterable.
                if UNKNOWN_LIST_TYPE in iterable_type or EMPTY_LIST_TYPE in iterable_type:
                    new_iterable_type.update(possible_list_types)

                else:
                    for list_type in possible_list_types:
                        if list_type in iterable_type:
                            new_iterable_type.add(list_type)
                

                if t_h.contains(iterable_type, "text") and t_h.contains(returned_element_type, "text"):
                    new_iterable_type.add("text")

                if not new_iterable_type:
                    raise Exception(
                                    f"ForAll: iterator type narrowed to '{returned_element_type}', "
                                    f"but iterable type '{iterable_type}' cannot support that."
                                    )
               
                self.iterable.inference(v_table=v_table,
                                        f_table=f_table,
                                        inference_context=inference_context,
                                        old_inference_value=iterable_type.copy(),
                                        new_inference_value=new_iterable_type.copy()
                                        )
                self.child_return_types["iterable"] = (new_iterable_type.copy(), self.iterable)
                vvvprint(f"ForAll: Inference successful, iterable type updated to '{new_iterable_type}' based on returned element type '{returned_element_type}'.")
                        
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
        
    def inference(
            v_table: ScopeStack,
            f_table: FuncTable,
            inference_context: InferenceContext,
            old_inference_value: set[str],
            new_inference_value: set[str]) -> None:
        raise Exception("ForAll does not return a value and cannot be used in inference.")

@dataclass
class RepeatUntil(ASTNode):
    condition: ASTNode
    body: Block
    def __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        try:
            self.child_return_types.clear()
            vvvprint("RepeatUntil: Checking repeat until statement...")

            condition_type = self.condition.check(
                v_table=v_table, 
                f_table=f_table,
                inference_context=inference_context
            )
            vvvprint(f"RepeatUntil: Condition type is '{condition_type}'.")
            
            valid_condition_type = {"boolean"}
            

            if not t_h.contains(condition_type, "boolean"):
                raise Exception(f"Condition in repeat until statement must be of type 'boolean', got '{condition_type}'")
            
            if condition_type != valid_condition_type:
                self.condition.inference(
                    v_table=v_table,
                    f_table=f_table,
                    inference_context=inference_context,
                    old_inference_value=condition_type.copy(),
                    new_inference_value=valid_condition_type.copy()
                )
                condition_type = valid_condition_type
            self.child_return_types["condition"] = (condition_type.copy(), self.condition)
            
            saved_inference_state = inference_context.save_state()
            
            v_table.new_scope()

            while True:
                vvvprint("RepeatUntil: Checking body of repeat until statement...")

                inference_context.reset()
                self.body.check(
                    v_table=v_table, 
                    f_table=f_table,
                    inference_context=inference_context
                )
                if not inference_context.has_changed():
                    vvvprint("RepeatUntil: Inference for body of repeat until statement has stabilized.")
                    break

                vvvprint("RepeatUntil: Inference for body of repeat until statement has changed, re-checking...")

            v_table.exit_scope()
            inference_context.load_state(saved_inference_state)
            vvvprint("RepeatUntil: Repeat until statement check successful.")
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
        
    def inference(self,
            v_table: ScopeStack,
            f_table: FuncTable,
            inference_context: InferenceContext,
            old_inference_value: set[str],
            new_inference_value: set[str]) -> None:
        raise Exception("RepeatUntil does not return a value and cannot be used in inference.")

@dataclass
class Quit(ASTNode):
    def __post_init__(self):
        super().__init__()
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        self.child_return_types.clear()
        vvvprint("Quit: Checking quit statement...")
        return
    
    def execute(self, env: Environment) -> None:
        raise SystemExit()
    
    def inference(
            v_table: ScopeStack,
            f_table: FuncTable,
            inference_context: InferenceContext,
            old_inference_value: set[str],
            new_inference_value: set[str]) -> None:
        raise Exception("Quit does not return a value and cannot be used in inference.")


@dataclass
class ListAdd(ASTNode):
    target: ASTNode
    item: ASTNode
    def __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        try:
            self.child_return_types.clear()
            vvvprint("ListAdd: Checking add list statement...")

            target_type = self.target.check(
                v_table,
                f_table, 
                inference_context
                )

            item_type = self.item.check(
                v_table, 
                f_table, 
                inference_context
                )
            if target_type is None:
                raise Exception(f"Target of add to list statement cannot be of type 'None'", self)
            if item_type is None:
                raise Exception(f"Item to add in add to list statement cannot be of type 'None'", self)
            if not t_h.has_list_type(target_type):
                raise Exception(f"Target of /'add to list/' statement must be a list type, got '{target_type}'", self)
            if item_type is None:
                raise Exception(f"Item to add in add to list statement cannot be of type 'None'", self)
            vvvprint(f"ListAdd: Target type is '{target_type}', item type is '{item_type}'.")
            
            

            list_element_types = t_h.get_list_element_types(target_type)
            if not t_h.is_compatible(item_type, list_element_types):
                raise Exception(
                    f"Item type '{item_type}' is not compatible with list element types '{list_element_types}' for target type '{target_type}' in list add statement.",
                    self
                    )
            
            narrowed_item_type = t_h.narrow(item_type, list_element_types)
            if narrowed_item_type != item_type:
                self.item.inference(
                    v_table=v_table,
                    f_table=f_table,
                    inference_context=inference_context,
                    old_inference_value=item_type.copy(),
                    new_inference_value=narrowed_item_type.copy()
                    )
                
                item_type = narrowed_item_type
                
            self.child_return_types["item"] = (item_type.copy(), self.item)

            new_target_type = t_h.make_set_list_types(item_type)

            if new_target_type != target_type:
                self.target.inference(
                    v_table=v_table,
                    f_table=f_table,
                    inference_context=inference_context,
                    old_inference_value=target_type.copy(),
                    new_inference_value=new_target_type.copy()
                    )
                
                target_type = new_target_type

            self.child_return_types["target"] = (target_type.copy(), self.target)
            vvvprint(f"ListAdd: List add statement check successful with target type '{target_type}' and item type '{item_type}'.")
            

        except Exception as e:
            raise TraceError(node = self, cause = e)

    def execute(self, env: Environment) -> None:
        try:
            target_value = self.target.execute(env)
            item_value = self.item.execute(env)
            target_value.append(item_value)
        except Exception as e:
            raise TraceError(node = self, cause = e)
        
    def inference(self,
            v_table: ScopeStack,
            f_table: FuncTable,
            inference_context: InferenceContext,
            old_inference_value: set[str],
            new_inference_value: set[str]) -> None:
        raise Exception("ListAdd does not return a value and cannot be used in inference.")


@dataclass
class ListRemove(ASTNode):
    target: ASTNode
    item: ASTNode
    def __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        try:
            self.child_return_types.clear()
            vvvprint("ListRemove: Checking add list statement...")

            target_type = self.target.check(
                v_table,
                f_table, 
                inference_context
                )

            item_type = self.item.check(
                v_table, 
                f_table, 
                inference_context
                )
            if target_type is None:
                raise Exception(f"Target of statement cannot be of type 'None'", self)
            if item_type is None:
                raise Exception(f"Item to remove from list statement cannot be of type 'None'", self)
            if not t_h.has_list_type(target_type):
                raise Exception(f"Target of remove from list statement must be a list type, got '{target_type}'", self)
            if item_type is None:
                raise Exception(f"Item to remove from list statement cannot be of type 'None'", self)
            vvvprint(f"ListRemove: Target type is '{target_type}', item type is '{item_type}'.")
            
            

            list_element_types = t_h.get_list_element_types(target_type)
            if not t_h.is_compatible(item_type, list_element_types):
                raise Exception(
                    f"Item type '{item_type}' is not compatible with list element types '{list_element_types}' for target type '{target_type}' in remove from list statement.",
                    self
                    )
            
            narrowed_item_type = t_h.narrow(item_type, list_element_types)
            if narrowed_item_type != item_type:
                self.item.inference(
                    v_table=v_table,
                    f_table=f_table,
                    inference_context=inference_context,
                    old_inference_value=item_type.copy(),
                    new_inference_value=narrowed_item_type.copy()
                    )
                
                item_type = narrowed_item_type
                
            self.child_return_types["item"] = (item_type.copy(), self.item)

            new_target_type = t_h.make_set_list_types(item_type)

            if new_target_type != target_type:
                self.target.inference(
                    v_table=v_table,
                    f_table=f_table,
                    inference_context=inference_context,
                    old_inference_value=target_type.copy(),
                    new_inference_value=new_target_type.copy()
                    )
                
                target_type = new_target_type

            self.child_return_types["target"] = (target_type.copy(), self.target)
            vvvprint(f"ListRemove: remove from list statement check successful with target type '{target_type}' and item type '{item_type}'.")

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
            
    def inference(
            self,
            v_table: ScopeStack,
            f_table: FuncTable,
            inference_context: InferenceContext,
            old_inference_value: set[str],
            new_inference_value: set[str]) -> None:
        raise Exception("ListRemove does not return a value and cannot be used in inference.")
        
@dataclass
class ListRemoveAt(ASTNode):
    target: ASTNode
    index: ASTNode
    def __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        try:
            self.child_return_types.clear()
            vvvprint("ListRemoveAt: Checking remove from list at statement...")
            
            target_type = self.target.check(
                v_table=v_table, 
                f_table=f_table,
                inference_context=inference_context
                )
            
            index_type = self.index.check(
                v_table=v_table, 
                f_table=f_table,
                inference_context=inference_context
                )
            vvvprint(f"ListRemoveAt: Target type is '{target_type}', index type is '{index_type}'.")
            
            if target_type is None:
                raise Exception(f"Target of statement cannot be of type 'None'", self)
            if index_type is None:
                raise Exception(f"Index in remove from list at statement cannot be of type 'None'", self)
            if not t_h.has_list_type(target_type):
                raise Exception(f"Target of remove from list at statement must be a list type, got '{target_type}'")
            if not t_h.contains(index_type, "number"):
                raise Exception(f"Index in remove from list at statement must be of type 'number', got '{index_type}'")
            
            if index_type != {"number"}:
                self.index.inference(
                    v_table=v_table,
                    f_table=f_table,
                    inference_context=inference_context,
                    old_inference_value=index_type.copy(),
                    new_inference_value={"number"}
                )

                index_type = {"number"}

            self.child_return_types["index"] = (index_type.copy(), self.index)
            if t_h.has_non_list_type(target_type):
                valid_target_type = t_h.get_all_list_types(target_type)
                self.target.inference(
                    v_table=v_table,
                    f_table=f_table,
                    inference_context=inference_context,
                    old_inference_value=target_type.copy(),
                    new_inference_value=valid_target_type.copy()
                )

                target_type = valid_target_type

            vvvprint(f"ListRemoveAt: remove from list at statement check successful with target type '{target_type}' and index type '{index_type}'.")
            self.child_return_types["target"] = (target_type.copy(), self.target)
            
            return None

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
        
    def inference(
            self,
            v_table: ScopeStack,
            f_table: FuncTable,
            inference_context: InferenceContext,
            old_inference_value: set[str],
            new_inference_value: set[str]) -> None:
        raise Exception("ListRemoveAt does not return a value and cannot be used in inference.")

@dataclass
class Return(ASTNode):
    expression: ASTNode
    def __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> Optional[set[str]]:
        try:
            self.child_return_types.clear()
            vvvprint("Return: Checking return statement...")

            return_type = self.expression.check(
                v_table=v_table,
                f_table=f_table,
                inference_context=inference_context
            )
            
            self.child_return_types["expression"] = (return_type.copy(), self.expression)
            self.child_return_types["self"] = (return_type, self)
            vvvprint(f"Return: Return statement check successful with return type '{return_type}'.")
            return return_type
        except Exception as e:
            raise TraceError(node = self, cause = e)

    def execute(self, env: Environment) -> Any:
        try:
            value = self.expression.execute(env)
            return value
        except Exception as e:
            raise TraceError(node = self, cause = e)
        
    def inference(
            self,
            v_table: ScopeStack,
            f_table: FuncTable,
            inference_context: InferenceContext,
            old_inference_value: set[str],
            new_inference_value: set[str]) -> None:
        raise Exception("Return does not return a value and cannot be used in inference.")