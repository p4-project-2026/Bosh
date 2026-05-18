from .ast_base import *
from os import path

@dataclass
class GoTo(ASTNode):
    path: ASTNode

    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        try:
            path_type = self.path.check(v_table, f_table, inference_context)
            if path_type not in ["folder", "text"]:
                raise TraceError(node = self, cause = f"Path in 'go to' statement must be of type 'text', got '{path_type}'")
        except Exception as e:
            raise TraceError(node = self, cause = e)

    def execute(self, env: Environment) -> None:
        return
        path_value = self.path.execute(env)
        if  path.isdir(path):
            env.go_to(path.abspath(path_value))
        else:
            raise TraceError(node = self, cause = f"Path '{path_value}' does not exist or is not a directory.")


@dataclass
class Make(ASTNode):
    entity_type: str
    name: ASTNode
    location: ASTNode
    new: bool = False
    def __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        try:
            if self.entity_type != "text":
                raise TraceError(node = self, cause = f"Entity type in make statement must be 'text', got '{self.entity_type}'")

            location_type = self.location.check(v_table, f_table, inference_context) if self.location else "text"

            if location_type != "text":
                raise TraceError(node = self, cause = f"Path in make statement must be of type 'text', got '{location_type}'")

            try:
                v_table.bind(self.name.name, self.entity_type)
            except Exception as e:
                raise TraceError(node = self, cause = e)

            name_type = self.name.check(v_table, f_table, inference_context)
            if name_type is not None and name_type != "text":
                raise TraceError(node = self, cause = f"Cannot use type '{name_type}' as a new name. Expected 'text'.")
        except Exception as e:
            raise TraceError(node = self, cause = e)

    def execute(self, env: Environment) -> None:
        # name_value = self.name.execute(env)
        # location_value = self.location.execute(env) if self.location else env.get_current_path()
        pass  # TODO: Implement logic to create the folder/file at the specified location
        

@dataclass
class Delete(ASTNode):
    target: ASTNode
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        try:
            target_type = self.target.check(v_table, f_table, inference_context)
            if target_type != "text":
                raise TraceError(node = self, cause = f"Cannot delete type '{target_type}'. Expected 'text'.")
        except Exception as e:
            raise TraceError(node = self, cause = e)
        
    def execute(self, env: Environment) -> None:
        target_value = self.target.execute(env)
        


@dataclass
class Rename(ASTNode):
    target: ASTNode
    new_name: ASTNode
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        try:
            target_type = self.target.check(v_table, f_table, inference_context)
            new_name_type = self.new_name.check(v_table, f_table, inference_context)
            if target_type != "text":
                raise TraceError(node = self, cause = f"Cannot rename type '{target_type}'. Expected 'text'.")
            if new_name_type != "text":
                raise TraceError(node = self, cause = f"New name must be of type 'text', got '{new_name_type}'")
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class Copy(ASTNode):
    source: ASTNode
    target: ASTNode
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        try:
            source_type = self.source.check(v_table, f_table, inference_context)
            target_type = self.target.check(v_table, f_table, inference_context)
            if source_type != "text":
                raise TraceError(node = self, cause = f"Cannot copy type '{source_type}'. Expected 'text'.")
            if target_type != "text":
                raise TraceError(node = self, cause = f"Target location in copy statement must be of type 'text', got '{target_type}'")
        except Exception as e:
            raise TraceError(node = self, cause = e)
        

@dataclass
class Move(ASTNode):
    source: ASTNode
    target: ASTNode
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        try:
            source_type = self.source.check(v_table, f_table, inference_context)
            target_type = self.target.check(v_table, f_table, inference_context)
            if source_type != "text":
                raise TraceError(node = self, cause = f"Cannot move type '{source_type}'. Expected 'text'.")
            if target_type != "text":
                raise TraceError(node = self, cause = f"Target location in move statement must be of type 'text', got '{target_type}'")
        except Exception as e:
            raise TraceError(node = self, cause = e)   


@dataclass
class Read(ASTNode):
    source: ASTNode
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        try:
            source_type = self.source.check(v_table, f_table, inference_context)
            if source_type != "text":
                raise TraceError(node = self, cause = f"Cannot read type '{source_type}'. Expected 'text'.")
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class Write(ASTNode):
    target: ASTNode
    data: ASTNode
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None: 
        try:
            target_type = self.target.check(v_table, f_table, inference_context)
            data_type = self.data.check(v_table, f_table, inference_context)
            if target_type != "text":
                raise TraceError(node = self, cause = f"Cannot write to type '{target_type}'. Expected 'text'.")
            if data_type != "text":
                raise TraceError(node = self, cause = f"Data in write statement must be of type 'text', got '{data_type}'")
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class GoUp(ASTNode):
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        return


@dataclass
class Execute(ASTNode):
    target: ASTNode
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        try:
            target_type = self.target.check(v_table, f_table, inference_context)
            if target_type != "text":
                raise TraceError(node = self, cause = f"Cannot execute type '{target_type}'. Expected 'text'.")
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class Pause(ASTNode):
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        return


@dataclass
class Wait(ASTNode):
    time: ASTNode
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        try:
            duration_type = self.time.check(v_table, f_table, inference_context)
            if duration_type not in ["number", "decimal", "time"]:
                raise TraceError(node = self, cause = f"Duration in 'wait' must be of type 'number', 'decimal' or 'time', got '{duration_type}'")
        except Exception as e:
            raise TraceError(node = self, cause = e)
        

@dataclass
class Input(ASTNode):
    prompt: Optional[ASTNode]
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> Optional[str]:
        try:
            prompt_type = self.prompt.check(v_table, f_table, inference_context) if self.prompt else None
            if prompt_type != "text":
                raise TraceError(node = self, cause = f"Prompt in input statement must be of type 'text', got '{prompt_type}'")
            return "text"
        except Exception as e:
            raise TraceError(node = self, cause = e)