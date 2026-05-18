from .ast_base import *
from os import path

@dataclass
class GoTo(ASTNode):
    path: ASTNode
    def __post_init__(self):
        super().__init__()

    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        try:
            self.child_return_types.clear()
            vvprint(f"Checking: 'go to' statement with path '{self.path}'...")

            path_type = self.path.check(
                v_table=v_table, 
                f_table=f_table, 
                inference_context=inference_context
            )
            if not path_type:
                raise Exception("Unable to determine type of path in 'go to' statement.")
            if not t_h.is_compatible(path_type, {"folder", "text"}):
                raise Exception(f"Path in 'go to' statement must be of type 'text' or 'folder', got '{path_type}'")
            narrowed_path_type = t_h.narrow(path_type, {"folder", "text"})
            if narrowed_path_type != path_type:
                self.path.inference(
                    v_table=v_table,
                    f_table=f_table, 
                    inference_context=inference_context, 
                    old_inference_value=path_type, 
                    new_inference_value=narrowed_path_type
                )
                path_type = narrowed_path_type
            
            self.child_return_types[self.path] = (path_type, self.path)
            vvvprint(f"Go to statement checked successfully with path type '{narrowed_path_type}'")

        except Exception as e:
            raise TraceError(node = self, cause = e)

    def execute(self, env: Environment) -> None:
        return
        path_value = self.path.execute(env)
        if  path.isdir(path):
            env.go_to(path.abspath(path_value))
        else:
            raise TraceError(node = self, cause = f"Path '{path_value}' does not exist or is not a directory.")
        
    def inference(
            self, 
            v_table, 
            f_table, 
            inference_context, 
            old_inference_value, 
            new_inference_value
            ) -> None:
        raise Exception("Inference should not be called on 'go to' statements since they do not produce a value.")


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
            self.child_return_types.clear()

            
            if not self.entity_type:
                raise Exception("Entity type in make statement cannot be empty.")
            
            if self.entity_type not in ["folder", "file"]:
                # I don't think this is correct, but anyway.
                raise Exception(f"Invalid entity type '{self.entity_type}' in make statement. Must be 'folder' or 'file'.")

            name_type = self.name.check(
                v_table, 
                f_table, 
                inference_context
            )
            
            if not t_h.contains(name_type, "text"):
                raise Exception(f"Name in make statement must be of type 'text', got '{name_type}'")
            
            location_type = self.location.check(
                v_table, 
                f_table, 
                inference_context
            )

            if not t_h.contains(location_type, "text"):
                raise Exception(f"Location in make statement must be of type 'text', got '{location_type}'")
            


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
        
    def inference(
            self, 
            v_table, 
            f_table, 
            inference_context, 
            old_inference_value, 
            new_inference_value
            ) -> None:
        raise Exception("Inference should not be called on 'make' statements since they do not produce a value.")   

@dataclass
class Delete(ASTNode):
    target: ASTNode
    def __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        try:
            self.child_return_types.clear()
            if self.target is None:
                raise Exception("Delete statement requires a target.")
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