from .ast_base import *
from .ast_expressions import Identifier
from ..semantics.func_table import FunctionSignature

@dataclass
class Assign(ASTNode):
    target: Identifier
    value: ASTNode
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        try:
            vvvprint(f"Assign: Checking assignment of value '{self.value}' to variable '{self.target.name}'...")
            value_type = self.value.check(v_table, f_table)
            vvvprint(f"Assign: Value '{self.value}' has type '{value_type}'")
            if value_type is None:
                raise BoshTypeError(f"Value assigned to '{self.target.name}' is undefined.", self)
            vvvprint(f"Assign: Attempting to bind variable '{self.target.name}' to type '{value_type}'...")
            value_type = self.value.check(v_table, f_table)
            if value_type is None:
                raise TraceError(node = self, cause = f"Value assigned to '{self.target.name}' is undefined.")
            vvvprint(f"Assign: Successfully bound variable '{self.target.name}' to type '{value_type}'.")
            v_table.bind(self.target.name, value_type)
            vvvprint(f"Assign: Variable '{self.target.name}' bound to type '{value_type}' successfully.")
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


@dataclass
class AssignType(ASTNode):
    target: ASTNode
    var_type: ASTNode
    value: Optional[ASTNode]
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        try:
            vvvprint(f"AssignType: Checking assignment of value '{self.value}' to variable '{self.target}' with declared type '{self.var_type}'...")
            value_type = self.value.check(v_table, f_table) if self.value else None
            var_type = self.var_type.check(v_table, f_table)
            vvvprint(f"AssignType: Value '{self.value}' has type '{value_type}'")
            if value_type and value_type != var_type:
                raise BoshTypeError(f"Cannot assign value of type '{value_type}' to variable '{self.target.name}' of type '{var_type}'", self)
            vvvprint(f"AssignType: Attempting to bind variable '{self.target.name}' to type '{var_type}'...")
            vvvprint(f"AssignType: Successfully bound variable '{self.target.name}' to type '{var_type}'.")
            v_table.bind(self.target.name, var_type)
            vvvprint(f"AssignType: Variable '{self.target.name}' bound to type '{var_type}' successfully.")
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
                
    
@dataclass
class TaskDecl(ASTNode):
    name: str
    parameters: List[str]
    body: Block
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        try:
            "TODO: Refactor to type check the body first to determine the return type, then bind the function signature with the correct return type, then type check the body again to ensure it matches the signature"
            vvvprint(f"TaskDecl: Checking task declaration of '{self.name}' with parameters {self.parameters}...")
            param_types = {param: "any" for param in self.parameters}
            signature = FunctionSignature(parameters=param_types, return_type="any")
            vvvprint(f"TaskDecl: Created function signature for task '{self.name}': {signature}")
            vvvprint(f"TaskDecl: Attempting to bind task '{self.name}' with signature {signature} in function table...")
            f_table.bind(self.name, signature)
            vvvprint(f"TaskDecl: Task '{self.name}' bound successfully in function table.")
            vvvprint(f"TaskDecl: Entering new scope for task '{self.name}' body checking...")
            v_table.new_scope()
            vvvprint(f"TaskDecl: New scope entered for task '{self.name}'. Checking task body...")
            vvvprint(f"TaskDecl: Binding parameters {self.parameters} to type 'any' in task '{self.name}' scope...")
            for param in self.parameters:
                v_table.bind(param, "any")
            vvvprint(f"TaskDecl: Parameters {self.parameters} bound successfully in task '{self.name}' scope. Checking task body...")
            body_type = self.body.check(v_table, f_table)
            vvvprint(f"TaskDecl: Task body checked. Determined return type: {body_type}")
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