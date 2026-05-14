from .ast_base import *
from .ast_expressions import Identifier
from ..semantics.func_table import FunctionSignature

@dataclass
class Assign(ASTNode):
    target: Identifier
    value: ASTNode
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        try:
            value_type = self.value.check(v_table, f_table)
            if value_type is None:
                raise TraceError(node = self, cause = f"Value assigned to '{self.target.name}' is undefined.")
            v_table.bind(self.target.name, value_type)
        except Exception as e:
            raise TraceError(node = self, cause = e)

    def execute(self, env: Environment) -> None:
        try:
            value = self.value.execute(env)
            env.assign_variable(self.target.name, value)
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class AssignType(ASTNode):
    target: ASTNode
    var_type: str
    value: Optional[ASTNode]
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        try:
            value_type = self.value.check(v_table, f_table) if self.value else None
            if value_type and value_type != self.var_type:
                raise TraceError(node = self, cause = f"Cannot assign value of type '{value_type}' to variable '{self.target.name}' of type '{self.var_type}'")

            v_table.bind(self.target.name, self.var_type)
        except Exception as e:
            raise TraceError(node = self, cause = e)
            
    def execute(self, env: Environment) -> None:
        try:
            env.assign_variable(self.target.name, self.value.execute(env) if self.value else None)
        except Exception as e:
            raise TraceError(node = self, cause = e)
                
    
@dataclass
class TaskDecl(ASTNode):
    name: str
    parameters: List[str]
    body: Block
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        try:
            param_types = {param: "any" for param in self.parameters}
            signature = FunctionSignature(parameters=param_types, return_type="any")

            f_table.bind(self.name, signature)
            v_table.new_scope()

            for param in self.parameters:
                v_table.bind(param, "any")

            body_type = self.body.check(v_table, f_table)
            signature.return_type = body_type if body_type else "any"
            v_table.exit_scope()
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