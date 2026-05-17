from .ast_base import *
from .ast_expressions import Identifier
from ..semantics.func_table import FunctionSignature

@dataclass
class Assign(ASTNode):
    target: Identifier
    value: ASTNode
    def __post_init__(self):
        super().__init__()

    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
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
                return
                
        except Exception as e:
            raise TraceError(node = self, cause = e)

    def execute(self, env: Environment) -> None:
        try:
            vvvprint(f"Assign: Executing assignment of value '{self.value}' to variable '{self.target.name}'...")
            value = self.value.execute(env)
            vvvprint(f"Assign: Attempting to assign value '{value}' to variable '{self.target.name}' in environment...")
            env.assign_variable(self.target.name, value)
            vvvprint(f"Assign: Successfully assigned value '{value}' to variable '{self.target.name}' in environment.")
        except Exception as e:
            raise TraceError(node = self, cause = e)
    
    def inference(
                v_table: ScopeStack,
                f_table: FuncTable,
                old_inference_value: set[str],
                new_inference_value: set[str]) -> None:
        raise Exception("Assign does not return a value and cannot be used in inference.")


@dataclass
class AssignType(ASTNode):
    target: ASTNode
    var_type: str
    value: Optional[ASTNode]
    def __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        try:
            self.child_return_types.clear()

            declared_type = {self.var_type}

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
            else:
                v_table.bind(self.target.name, declared_type.copy())

        except Exception as e:
            raise TraceError(node = self, cause = e)
            
    def execute(self, env: Environment) -> None:
        vvvprint(f"AssignType: Executing assignment of value '{self.value}' to variable '{self.target.name}' with declared type '{self.var_type}'...")
        try:
            vvvprint(f"AssignType: Attempting to assign value '{self.value}' to variable '{self.target.name}' in environment...")
            env.assign_variable(self.target.name, self.value.execute(env) if self.value else None)
            vvvprint(f"AssignType: Successfully assigned value '{self.value}' to variable '{self.target.name}' in environment.")
        except Exception as e:
            raise TraceError(node = self, cause = e)
                
    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                inference_context: InferenceContext,
                old_inference_value: set[str],
                new_inference_value: set[str]) -> None:
        raise Exception(f"AssignType does not return a value and cannot be used in inference.", self)


@dataclass
class TaskDecl(ASTNode):
    name: str
    parameters: List[str]
    body: Block
    def __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        try:
            self.child_return_types.clear()
            saved_inference_state = inference_context.save_state()
            v_table.new_scope()
            for param in self.parameters:
                v_table.bind(param, {UNKNOWN_TYPE})
            
            return_type = None
            while True:
                vvvprint(f"TaskDecl: Starting inference iteration for task '{self.name}'...")

                inference_context.reset()

                return_type = self.body.check(
                    v_table=v_table, 
                    f_table=f_table, 
                    inference_context=inference_context
                    )
                
                if not inference_context.has_changed():
                    vvvprint(f"TaskDecl: No changes in inference context after checking body of task '{self.name}', breaking inference loop.")
                    break
                

            
            parameter_dict = {param: v_table.lookup(param) for param in self.parameters}
            f_table.bind(
                self.name,
                FunctionSignature(
                    parameters=parameter_dict,
                    return_type=return_type
                )
            )
            vvvprint(f"TaskDecl: Task '{self.name}' bound successfully to function table with signature: parameters {parameter_dict} and return type '{return_type}'.")
            v_table.exit_scope()
            inference_context.load_state(saved_inference_state)
        except Exception as e:
            raise TraceError(node = self, cause = e)
            
    def execute(self, env: Environment) -> None:
        try:
            # Create a snapshot of the current variable scope stack to capture the environment for the function
            env_snapshot = env.snapshot()
            # Create a FunctionBinding for the task and bind it to the function table
            function_binding = FunctionBinding(parameters=self.parameters, body=self.body, captured_scope=env_snapshot)

            env.bind_function(self.name, function_binding)
        except Exception as e:
            raise TraceError(node = self, cause = e)
        
    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                inference_context: InferenceContext,
                old_inference_value: set[str],
                new_inference_value: set[str]) -> None:
        raise Exception(f"TaskDecl: does not return a value and cannot be used in inference. something went wrong in inference pathing.", self)