from bosh.interpreter.semantics.symbol_table import Symbol_Table

from .ast_base import *
from .ast_expressions import Identifier
from ..semantics.func_table import FunctionSignature


@dataclass
class Assign(ASTNode):
    target: Identifier
    value: ASTNode
    def __post_init__(self):
        super().__init__()


    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking assignment of value '{self.value}' to variable '{self.target.name}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context, value_type: (
                f"Assignment of value '{self.value}' to variable '{self.target.name}' type checked successfully with value type '{value_type}'."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> None:
        try:
            self.child_return_types.clear()

            value_type = self.value.check(
                v_table=v_table,
                f_table=f_table, 
                inference_context=inference_context
                )
            if value_type is None:
                raise Exception(f"Value assigned to '{self.target.name}' is undefined.", self)
            
            if v_table.contains(self.target.name):
                old_types = v_table.lookup(self.target.name)
                if not t_h.is_compatible(old_types, value_type):
                    raise Exception(f"Cannot assign value of type '{value_type}' to variable '{self.target.name}' of type '{old_types}'", self)
                
                narrowed_type = t_h.narrow(old_types, value_type)
                if narrowed_type != value_type:
                    self.value.inference(
                        v_table=v_table,
                        f_table=f_table,
                        inference_context=inference_context,
                        old_inference_value=value_type.copy(),
                        new_inference_value=narrowed_type.copy()
                        )
                    
                if old_types != narrowed_type:
                    v_table.bind(self.target.name, narrowed_type.copy())
                    inference_context.mark_infered()
                    
                self.child_return_types["value"] = (narrowed_type.copy(), self.value)
                return
            else:
                v_table.bind(self.target.name, value_type.copy())
                self.child_return_types["value"] = (value_type.copy(), self.value)
                log_case.set("success", value_type=value_type.copy())
                return
                
        except Exception as e:
            raise TraceError(node = self, cause = e)


    @logged(
        start=lambda self, env: (
            f"Executing assignment of value '{self.value}' to variable '{self.target.name}'..."
        ),
        success={
            "success": lambda self, env: (
                f"Assignment of value '{self.value}' to variable '{self.target.name}' executed successfully."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> None:
        try:
            value = self.value.execute(env)
            env.assign_variable(self.target.name, value)
            log_case.set("success")
        except Exception as e:
            raise TraceError(node = self, cause = e)
    

@dataclass
class AssignType(ASTNode):
    target: ASTNode
    var_type: ASTNode
    value: Optional[ASTNode]
    def __post_init__(self):
        super().__init__()
    

    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking assignment of type '{self.var_type}' to variable '{self.target.name}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context, return_type: (
                f"Assignment of type '{self.var_type}' to variable '{self.target.name}' checked successfully with return type: {return_type}"
             )
         }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> None:
        try:
            
            self.child_return_types.clear()
    
            declared_type = self.var_type.check(v_table, f_table, inference_context)
            if declared_type is None:
                raise Exception(f"Declared type for variable '{self.target.name}' is undefined.", self)

            if self.value:
                value_type = self.value.check(
                    v_table=v_table,
                    f_table=f_table,
                    inference_context=inference_context,
                    )

                if value_type is None:
                    raise Exception(
                        f"Value assigned to '{self.target.name}' is undefined.",
                        self,
                        )

                if not t_h.is_compatible(declared_type, value_type):
                    raise Exception(
                        f"Cannot assign value of type '{value_type}' to variable "
                        f"'{self.target.name}' of type '{self.var_type}'",
                        self,
                        )

                narrowed_value_type = t_h.narrow(value_type, declared_type)

                if narrowed_value_type != value_type:
                    self.value.inference(
                        v_table=v_table,
                        f_table=f_table,
                        inference_context=inference_context,
                        old_inference_value=value_type.copy(),
                        new_inference_value=narrowed_value_type.copy(),
                        )

                self.child_return_types["value"] = (
                    narrowed_value_type.copy(),
                    self.value,
                    )

            if v_table.contains(self.target.name):
                old_type = v_table.lookup(self.target.name)

                if not t_h.is_compatible(old_type, declared_type):
                    raise Exception(
                        f"Cannot assign type '{self.var_type}' to variable "
                        f"'{self.target.name}' of type '{old_type}'",
                        self,
                        )

                narrowed_declared_type = t_h.narrow(old_type, declared_type)
                if narrowed_declared_type != old_type:
                    v_table.bind(self.target.name, narrowed_declared_type.copy())
                    inference_context.mark_infered()
                
                self.child_return_types["value"] = (
                    narrowed_declared_type.copy(),
                    self.value,
                    )
                log_case.set("success", value_type=narrowed_declared_type.copy())
            else:
                v_table.bind(self.target.name, declared_type.copy())

        except Exception as e:
            raise TraceError(node = self, cause = e)


    @logged(
        start=lambda self, env: (
            f"Executing assignment of type '{self.var_type}' to variable '{self.target.name}'..."
        ),
        success={
            "success": lambda self, env, value: (
                f"Assignment of value '{value}' to variable '{self.target.name}' executed successfully."
            )
        }
    )
    def execute(self, env: Environment, value: Any = None, *, log_case: LogCase) -> None:
        try:
            value = self.value.execute(env) if self.value else None
            env.assign_variable(self.target.name, value)
            log_case.set("success", value=value)

        except Exception as e:
            raise TraceError(node = self, cause = e)
                

@dataclass
class TaskDecl(ASTNode):
    name: str
    parameters: List[str]
    body: Block
    captured_scope: Optional[Symbol_Table] = None
    def __post_init__(self):
        super().__init__()
    

    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking task declaration for task '{self.name}' with parameters {self.parameters}..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context, return_type: (
                f"Task declaration for task '{self.name}' checked successfully with return type: {return_type}"
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> None:
        try:
            self.child_return_types.clear()
    
            saved_inference_state = inference_context.save_state()
            if self.captured_scope is None:
                self.captured_scope = v_table.snapshot()
                v_table.new_scope()
            else:
                v_table.update_snapshot(self.captured_scope)  # Update the snapshot with the current visible scopes so that it captures the correct environment for the function definition
                v_table.enter_function_scope(self.captured_scope)  # Enter the function scope to ensure parameters are bound in the correct scope for checking the function body
            
            
            for param in self.parameters:
                v_table.bind_local(param, {UNKNOWN_TYPE})
            
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
                
                vvvprint(f"TaskDecl: Detected a change during inference of task '{self.name}', restarting type checking of task body with updated types...")
            
            parameter_dict = {param: v_table.lookup(param) for param in self.parameters}
            f_table.bind(
                self.name,
                FunctionSignature(
                    parameters=parameter_dict,
                    return_type=return_type,
                    function_def=self
                )
            )

            self.child_return_types["body"] = (return_type, self.body)
            for param in self.parameters:
                self.child_return_types[param] = (parameter_dict[param], None)
            
            vvvprint(f"TaskDecl: Task '{self.name}' bound successfully to function table with signature: parameters {parameter_dict} and return type '{return_type}'.")
            v_table.exit_scope()
            inference_context.load_state(saved_inference_state)
            log_case.set("success", return_type=return_type)
        except Exception as e:
            raise TraceError(node = self, cause = e)
    

    @logged(
        start=lambda self, env: (
            f"Executing task declaration for task '{self.name}'..."
        ),
        success={
            "success": lambda self, env: (
                f"Task declaration for task '{self.name}' executed successfully and function binding created in environment."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> None:
        try:
            # Create a snapshot of the current variable scope stack to capture the environment for the function
            env_snapshot = env.snapshot()
            # Create a FunctionBinding for the task and bind it to the function table
            function_binding = FunctionBinding(parameters=self.parameters, body=self.body, captured_scope=env_snapshot)

            env.bind_function(self.name, function_binding)
            log_case.set("success")
        except Exception as e:
            raise TraceError(node = self, cause = e)
        
