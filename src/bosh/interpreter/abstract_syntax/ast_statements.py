from .ast_base import *
import os

@dataclass
class Print(ASTNode):
    expression: ASTNode
    def __post_init__(self):
        super().__init__()


    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking print statement..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context, expression_type: (
                f"Print statement checked successfully with expression type: {expression_type}"
             )
         }  
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> None:
        try:
            self.child_return_types.clear()
            expression_type = self.expression.check(
                v_table, 
                f_table, 
                inference_context
            )
            self.child_return_types["expression"] = (expression_type.copy(), self.expression)
            log_case.set("success", expression_type=expression_type)
            
        except Exception as e:
            raise TraceError(node = self, cause = e, hide_trace = True)


    @logged(
        start=lambda self, env: (
            f"Attempting to execute print statement..."
        ),
        success={
            "success": lambda self, env: (
                f"Print statement executed successfully."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> None:
        try:
            value = self.expression.execute(env)
            if t_h.has_only_list_types(self.child_return_types["expression"][0]):
                if t_h.is_only(self.child_return_types["expression"][0], "list<text>"):
                    print(f_h.string_format_list_of_strings(value))
                elif t_h.is_only(self.child_return_types["expression"][0], "list<boolean>"):
                    print(f_h.string_format_list_of_bools(value))
                else:
                    print(f_h.string_format_list(value))

            elif self.child_return_types["expression"][0] == {"boolean"}:
                print(f_h.string_format_bool(value))
            else:
                print(value)
            
            log_case.set("success")
        except Exception as e:
            raise TraceError(node = self, cause = e, hide_trace = True)


@dataclass
class IfElse(ASTNode):
    condition: ASTNode
    then_branch: Block
    else_branch: Optional[Block]
    def __post_init__(self):
        super().__init__()     


    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking if-else statement..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"If-else statement checked successfully."
                )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> None:
        try:
            self.child_return_types.clear()
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
            then_type = None
            else_type = None
            saved_inference_state = inference_context.save_state()
            v_table.new_scope()
            while True:
                inference_context.reset()
                then_type = self.then_branch.check(
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
                    else_type = self.else_branch.check(
                        v_table=v_table, 
                        f_table=f_table, 
                        inference_context=inference_context
                    )

                    if not inference_context.has_changed():
                        break

                v_table.exit_scope()
                
            return_type = None
            inference_context.load_state(saved_inference_state)
            if then_type is not None or else_type is not None:
                if then_type is None:
                    return_type = else_type
                elif else_type is None:
                    return_type = then_type
                elif then_type == else_type:
                    return_type = then_type
                else:
                    if t_h.is_compatible(then_type, else_type):
                        return_type = t_h.narrow(then_type, else_type)
                    else:
                        raise Exception(f"Then branch of if statement has incompatible type '{then_type}' with else branch type '{else_type}'")
            
            log_case.set("success")
            return return_type
        except Exception as e:
            raise TraceError(node = self, cause = e, hide_trace = True)


    @logged(
        start=lambda self, env: (
            f"Attempting to execute if-else statement..."
        ),
        success={
            "if_branch": lambda self, env, return_val: (
                f"If branch of if-else statement executed successfully."
            ),
            "else_branch": lambda self, env, return_val: (
                f"Else branch of if-else statement executed successfully."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> None:
        try:
            condition_value = self.condition.execute(env)
            value = None
            if condition_value:
                env.new_scope()
                value = self.then_branch.execute(env)
                env.exit_scope()
                log_case.set("if_branch", return_val=value)
            elif self.else_branch:
                env.new_scope()
                value = self.else_branch.execute(env)
                env.exit_scope()
                log_case.set("else_branch", return_val=value)
            return value
        except Exception as e:
            raise TraceError(node = self, cause = e, hide_trace = True)
        

@dataclass
class Fallback(ASTNode):
    primary_stmt: ASTNode
    fallback_stmt: ASTNode
    def __post_init__(self):
        super().__init__()
    

    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking fallback statement..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"Fallback statement checked successfully."
            )
        }
    )   
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> None:
        try:
            self.child_return_types.clear()
            self.primary_stmt.check(v_table=v_table, f_table=f_table, inference_context=inference_context)
            self.fallback_stmt.check(v_table=v_table, f_table=f_table, inference_context=inference_context)
            log_case.set("success")
        except Exception as e:
            raise TraceError(node = self, cause = e)


    @logged(
        start=lambda self, env: (
            f"Attempting to execute primary statement of fallback..."
        ),
        success={
            "success": lambda self, env: (
                f"Primary statement of fallback executed successfully."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> None:
        try:
            self.primary_stmt.execute(env)
            log_case.set("success")
        except Exception:
            try:
                self.fallback_stmt.execute(env)
                log_case.set("success")
            except Exception as e:
                raise TraceError(node = self, cause = e)


@dataclass
class ForAll(ASTNode):
    iterator_name: str
    iterable: ASTNode
    body: Block
    def __post_init__(self):
        super().__init__()


    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking for all statement..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"ForAll checked successfully."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> None:
        try:
            self.child_return_types.clear()
            

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
            return_type = None
            while True:
                inference_context.reset()
                return_type = self.body.check(
                    v_table=v_table,
                    f_table=f_table,
                    inference_context=inference_context
                )
                


                if not inference_context.has_changed():
                    break

                vvvprint("ForAll: Inference for body of for all statement has changed, re-checking...")

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
            log_case.set("success")
            return return_type

        except Exception as e:
            raise TraceError(node = self, cause = e)


    @logged(
        start=lambda self, env: (
            f"Executing for all statement..."
        ),
        success={
            "success": lambda self, env: (
                f"ForAll executed successfully."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> None:
        try:
            iterable_val = self.iterable.execute(env)
            
            elements_to_iterate = []
            if t_h.is_only(iterable_val, "text"):
                if not os.path.exists(iterable_val):
                    raise ValueError(f"Directory path '{iterable_val}' does not exist.")
                if not os.path.isdir(iterable_val):
                    raise ValueError(f"Path '{iterable_val}' is a file, not a directory.")
                
                for item in os.listdir(iterable_val):
                    full_path = os.path.join(iterable_val, item)
                    elements_to_iterate.append(full_path.replace("\\", "/"))
                    
            else:
                elements_to_iterate = iterable_val
            return_value = None
            for element in elements_to_iterate:
                env.new_scope()
                try:
                    env.assign_variable(self.iterator_name, element)
                    value = self.body.execute(env)
                    if isinstance(value, ContinueSignal):
                        value = None
                        continue
                    
                    elif isinstance(value, BreakSignal):
                        value = None
                        break
                    elif value is not None:
                        return_value = value
                        break

                finally:
                    env.exit_scope()           
            
            log_case.set("success")
            return return_value
        except Exception as e:
            raise TraceError(node = self, cause = e, hide_trace = True)
        

@dataclass
class RepeatUntil(ASTNode):
    condition: ASTNode
    body: Block
    def __post_init__(self):
        super().__init__()


    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking repeat until statement..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"RepeatUntil checked successfully."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> None:
        try:
            self.child_return_types.clear()

            condition_type = self.condition.check(
                v_table=v_table, 
                f_table=f_table,
                inference_context=inference_context
            )
            
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
            return_type = None
            while True:

                inference_context.reset()
                return_type = self.body.check(
                    v_table=v_table, 
                    f_table=f_table,
                    inference_context=inference_context
                )
                if not inference_context.has_changed():
                    break

                vvvprint("RepeatUntil: Inference for body of repeat until statement has changed, re-checking...")
            v_table.exit_scope()
            inference_context.load_state(saved_inference_state)
            log_case.set("success")
            return return_type
        except Exception as e:
            raise TraceError(node = self, cause = e)


    @logged(
        start=lambda self, env: (
            f"Executing repeat until statement..."
        ),
        success={
            "success": lambda self, env: (
                f"RepeatUntil executed successfully."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> None:
        try:
            value = None
            env.new_scope()
            while True:
                value = self.body.execute(env)
                condition_value = self.condition.execute(env)
                if isinstance(value, ContinueSignal):
                    value = None
                    continue
                elif isinstance(value, BreakSignal):
                    value = None
                    break
                elif value is not None:
                    break
                elif condition_value:
                    break
            env.exit_scope()
            log_case.set("success")
            return value
        except Exception as e:
            raise TraceError(node = self, cause = e)

        
@dataclass
class Count(ASTNode):
    iterator_name: Optional[str]
    from_: ASTNode
    to_: ASTNode
    body: Block
    def __post_init__(self):
        super().__init__()


    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking count statement..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"Count statement checked successfully."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> None:
        try:
            from_type = self.from_.check(
                v_table=v_table, 
                f_table=f_table, 
                inference_context=inference_context
            )
            
            to_type = self.to_.check(
                v_table=v_table, 
                f_table=f_table, 
                inference_context=inference_context
            )
            
            if from_type is None:
                raise Exception(f"'From' expression in count statement cannot be of type 'None'", self)
            if to_type is None:
                raise Exception(f"'To' expression in count statement cannot be of type 'None'", self)
            
            valid_count_types = {"number"}
            
            if not t_h.contains(from_type, "number"):
                raise Exception(f"'From' expression in count statement must be of type 'number', got '{from_type}'")
            if not t_h.contains(to_type, "number"):
                raise Exception(f"'To' expression in count statement must be of type 'number', got '{to_type}'")
            
            if from_type != valid_count_types:
                self.from_.inference(
                    v_table=v_table, 
                    f_table=f_table, 
                    inference_context=inference_context,
                    old_inference_value=from_type.copy(),
                    new_inference_value=valid_count_types.copy()
                )
                from_type = valid_count_types
            
            self.child_return_types["from"] = (from_type.copy(), self.from_)

            if to_type != valid_count_types:
                self.to_.inference(
                    v_table=v_table, 
                    f_table=f_table, 
                    inference_context=inference_context,
                    old_inference_value=to_type.copy(),
                    new_inference_value=valid_count_types.copy()
                )
                to_type = valid_count_types

            self.child_return_types["to"] = (to_type.copy(), self.to_)


                
            saved_inference_state = inference_context.save_state()

            v_table.new_scope()
            return_type = None
            if self.iterator_name:
                v_table.bind_local(self.iterator_name, {"number"})
            while True:
                inference_context.reset()
                return_type = self.body.check(
                    v_table=v_table, 
                    f_table=f_table,
                    inference_context=inference_context
                )
                if not inference_context.has_changed():
                    break
                
                vvvprint("Count: Inference for body of count statement has changed, re-checking...")

            v_table.exit_scope()
            inference_context.load_state(saved_inference_state)
            log_case.set("success")
            return return_type
        except Exception as e:
            raise TraceError(node = self, cause = e)


    @logged(
        start=lambda self, env: (
            f"Executing count statement..."
        ),
        success={
            "success": lambda self, env: (
                f"Count statement executed successfully."
            )   
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> None:
        try:
            value = None
            from_value = self.from_.execute(env)
            to_value = self.to_.execute(env)
            for i in range(from_value, to_value + 1):
                env.new_scope()
                if self.iterator_name:
                    try:
                        env.bind_local_variable(self.iterator_name, i)
                        value = self.body.execute(env)
                        if isinstance(value, ContinueSignal):
                            value = None
                            continue
                        if isinstance(value, BreakSignal):
                            value = None
                            break
                        if value is not None:
                            break
                    finally:
                        env.exit_scope()
                else:
                    try:
                        value = self.body.execute(env)
                        if isinstance(value, ContinueSignal):
                            value = None
                            continue
                        if isinstance(value, BreakSignal):
                            value = None
                            break
                        if value is not None:
                            break
                    finally:
                        env.exit_scope()
            
            log_case.set("success")
            return value
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class Quit(ASTNode):
    def __post_init__(self):
        super().__init__()


    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking quit statement..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"Quit statement checked successfully."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> None:
        self.child_return_types.clear()
        log_case.set("success")
        return


    @logged(
        start=lambda self, env: (
            f"Attempting to execute quit statement..."
        ),
        success={
            "success": lambda self, env: (
                f"Quit statement executed successfully, exiting program. Goodbye!"
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> None:
        log_case.set("success")
        raise SystemExit()

@dataclass
class ListAssign(ASTNode):
    target: ASTNode
    index: ASTNode
    value: ASTNode
    def __post_init__(self):
        super().__init__()

    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking list assignment statement..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"List assignment statement checked successfully."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> None:
        try:
            self.child_return_types.clear()
            target_type = self.target.check(v_table=v_table, f_table=f_table, inference_context=inference_context)
            if target_type is None:
                raise Exception(f"Target of list assignment cannot be of type 'None'")
            
            if not t_h.has_list_type(target_type):
                raise Exception(f"Target of list assignment must be a list type, got '{target_type}'")
            
            if t_h.has_non_list_type(target_type):
                new_target_type = t_h.get_all_list_types(target_type)
                self.target.inference(
                    v_table=v_table,
                    f_table=f_table,
                    inference_context=inference_context,
                    old_inference_value=target_type.copy(),
                    new_inference_value=new_target_type.copy()
                )
                target_type = new_target_type
            
            index_type = self.index.check(v_table=v_table, f_table=f_table, inference_context=inference_context)
            if index_type is None:
                raise Exception(f"Index in list assignment cannot be of type 'None'")
            
            if not t_h.contains(index_type, "number"):
                raise Exception(f"Index in list assignment must be of type 'number', got '{index_type}'")
            
            if index_type != {"number"}:
                self.index.inference(
                    v_table=v_table,
                    f_table=f_table,
                    inference_context=inference_context,
                    old_inference_value=index_type.copy(),
                    new_inference_value={"number"}
                )
                index_type = {"number"}

            value_type = self.value.check(v_table=v_table, f_table=f_table, inference_context=inference_context)

            if value_type is None:
                raise Exception(f"Value in list assignment cannot be of type 'None'")
            
            list_element_types = t_h.get_list_element_types(target_type)
            if not t_h.is_compatible(value_type, list_element_types):
                raise Exception(f"the type '{value_type}' is not compatible with the element type of the list  '{list_element_types}'.")

            if list_element_types != value_type:
                narrowed_value_type = t_h.narrow(value_type, list_element_types)
                self.value.inference(
                    v_table=v_table,
                    f_table=f_table,
                    inference_context=inference_context,
                    old_inference_value=value_type.copy(),
                    new_inference_value=narrowed_value_type.copy()
                )
                if narrowed_value_type != list_element_types:
                    new_target_type = t_h.make_set_list_types(narrowed_value_type)
                    self.target.inference(
                        v_table=v_table,
                        f_table=f_table,
                        inference_context=inference_context,
                        old_inference_value=target_type.copy(),
                        new_inference_value=new_target_type.copy()
                    )

                value_type = narrowed_value_type = narrowed_value_type

            self.child_return_types["target"] = (target_type.copy(), self.target)
            self.child_return_types["index"] = (index_type.copy(), self.index)
            self.child_return_types["value"] = (value_type.copy(), self.value)
            log_case.set("success")

        except Exception as e:
            raise TraceError(node = self, cause = e)

    @logged(
        start=lambda self, env: (
            f"Attempting to execute list assignment statement..."
        ),
        success={
            "success": lambda self, env: (
                f"List assignment statement executed successfully."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> None:
        try:
            target_value = self.target.execute(env)
            index_value = self.index.execute(env)
            value = self.value.execute(env)
            target_value[index_value] = value
            log_case.set("success")
        except Exception as e:
            raise TraceError(node = self, cause = e)
        
@dataclass
class ListAdd(ASTNode):
    op: str
    item: ASTNode
    target: ASTNode
    index: Optional[ASTNode] = None
    def __post_init__(self):
        super().__init__()


    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking {self.op} to list statement..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"{self.op.capitalize()} to list statement checked successfully."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> None:
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

            if self.op == "insert":
                if self.index is None:
                    raise Exception("Index must be provided for 'insert' operation in ListAdd statement.", self)
                
                index_type = self.index.check(
                    v_table=v_table,
                    f_table=f_table,
                    inference_context=inference_context
                )
                if index_type is None:
                    raise Exception(f"Index in insert to list statement cannot be of type 'None'", self)
                if not t_h.contains(index_type, "number"):
                    raise Exception(f"Index in insert to list statement must be of type 'number', got '{index_type}'", self)
                
                valid_index_type = {"number"}
                if index_type != valid_index_type:
                    self.index.inference(
                        v_table=v_table,
                        f_table=f_table,
                        inference_context=inference_context,
                        old_inference_value=index_type.copy(),
                        new_inference_value=valid_index_type.copy()
                    )
                    index_type = valid_index_type

                self.child_return_types["index"] = (index_type.copy(), self.index)

            log_case.set("success")

        except Exception as e:
            raise TraceError(node = self, cause = e)


    @logged(
        start=lambda self, env: (
            f"Executing {self.op} to list statement..."
        ),
        success={
            "success": lambda self, env: (
                f"{self.op.capitalize()} to list statement executed successfully."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> None:
        try:
            
            target_value = self.target.execute(env)

            item_value = self.item.execute(env)


            if self.op == "insert" and self.index is not None:
                index_value = self.index.execute(env)
                target_value.insert(index_value, item_value)

            elif self.op == "append":
                target_value.append(item_value)

            
            elif self.op == "prepend":

                target_value.insert(0, item_value)

            log_case.set("success")

        except Exception as e:
            raise TraceError(node = self, cause = e)
        

@dataclass
class ListRemove(ASTNode):
    target: ASTNode
    item: ASTNode
    def __post_init__(self):
        super().__init__()


    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking remove from list statement..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"Remove from list statement checked successfully."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> None:
        try:
            self.child_return_types.clear()

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
            log_case.set("success")

        except Exception as e:
            raise TraceError(node = self, cause = e)


    @logged(
        start=lambda self, env: (
            f"Executing remove from list statement..."
        ),
        success={
            "success": lambda self, env: (
                f"Remove from list statement executed successfully."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> None:
        try:
            target_value = self.target.execute(env)
            item_value = self.item.execute(env)
            while item_value in target_value:
                    target_value.remove(item_value)
            
            log_case.set("success")
            
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class ListRemoveAt(ASTNode):
    target: ASTNode
    index: ASTNode
    def __post_init__(self):
        super().__init__()


    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking remove from list at statement..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"Remove from list at statement checked successfully."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> None:
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
            
            log_case.set("success")
            return None

        except Exception as e:
            raise TraceError(node = self, cause = e)


    @logged(
        start=lambda self, env: (
            f"Executing remove from list at statement..."
        ),
        success={
            "success": lambda self, env: (
                f"Remove from list at statement executed successfully."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> None:
        try:
            target_value = self.target.execute(env)
            index_value = self.index.execute(env)
            try:
                del target_value[index_value]
                log_case.set("success")
            except IndexError:
                raise TraceError(node = self, cause = f"Index '{index_value}' out of range for list.")
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class Return(ASTNode):
    expression: ASTNode
    def __post_init__(self):
        super().__init__()


    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking return statement..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context, return_type: (
                f"Return statement checked successfully with return type '{return_type}'."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> Optional[set[str]]:
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
            log_case.set("success", return_type=return_type)
            return return_type
        except Exception as e:
            raise TraceError(node = self, cause = e)


    @logged(
        start=lambda self, env: (
            f"Executing return statement..."
        ),
        success={
            "return_val": lambda self, env, return_val: (
                f"Return statement executed successfully with return value: {return_val}"
             )
         }
    )
    def execute(self, env: Environment, log_case: LogCase) -> Any:
        try:
            value = self.expression.execute(env)
            log_case.set("return_val", return_val=value)    
            return value
        except Exception as e:
            raise TraceError(node = self, cause = e)
        
class Continue(ASTNode):


    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking continue statement..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"Continue statement checked successfully."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> None:
        log_case.set("success")
        return None


    @logged(
        start=lambda self, env: (
            f"Executing continue statement..."
        ),
        success={
            "success": lambda self, env: (
                f"Continue statement executed successfully."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> ContinueSignal:
        log_case.set("success")
        return ContinueSignal()

class Break(ASTNode):


    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking break statement..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"Break statement checked successfully."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> None:
        log_case.set("success")
        return None


    @logged(
        start=lambda self, env: (
            f"Executing break statement..."
        ),
        success={
            "success": lambda self, env: (
                f"Break statement executed successfully."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> BreakSignal:
        log_case.set("success")
        return BreakSignal()