import msvcrt
from .ast_base import *
import os
import time

@dataclass
class GoTo(ASTNode):
    path: ASTNode
    def __post_init__(self):
        super().__init__()

    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking 'go to' statement with path '{self.path}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context, path_type: (
                f"'Go to' statement checked successfully with path type '{path_type}'."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> None:
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

        except Exception as e:
            raise TraceError(node = self, cause = e)
    
    @logged(
        start=lambda self, env: (
            f"Executing 'go to' statement with path '{self.path}'..."
        ),
        success={
            "success": lambda self, env, path_value: (
                f"'Go to' statement executed successfully, current directory changed to '{path_value}'."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> None:
        try:
            path_value = self.path.execute(env)
            log_case.set("success", path_value=path_value)
            os.chdir(path_value)
        except Exception as e:
            raise TraceError(node = self, cause = e)
        return
        


@dataclass
class Make(ASTNode):
    new: bool
    entity_type: str
    name: ASTNode
    location: ASTNode
    def __post_init__(self):
        super().__init__()
    

    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking 'make' statement to create a new {self.entity_type} with name '{self.name}' and location '{self.location}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"'Make' statement checked successfully for creating a new {self.entity_type} with name '{self.name}' and location '{self.location}'."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> None:
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
            if name_type != {"text"}:
                self.name.inference(
                    v_table=v_table,
                    f_table=f_table, 
                    inference_context=inference_context, 
                    old_inference_value=name_type, 
                    new_inference_value={"text"}
                )
                
                name_type = {"text"}
                
            self.child_return_types[self.name] = (name_type, self.name)

            location_type = self.location.check(
                v_table, 
                f_table, 
                inference_context
            )

            if not t_h.contains(location_type, "text"):
                raise Exception(f"Location in make statement must be of type 'text', got '{location_type}'")
            
            if location_type != {"text"}:
                self.location.inference(
                    v_table=v_table,
                    f_table=f_table, 
                    inference_context=inference_context, 
                    old_inference_value=location_type, 
                    new_inference_value={"text"}
                )

                location_type = {"text"}

            self.child_return_types[self.location] = (location_type, self.location)
            log_case.set("success")

        except Exception as e:
            raise TraceError(node = self, cause = e)


    @logged(
        start=lambda self, env: (
            f"Executing 'make' statement to create a new {self.entity_type} with name '{self.name}' and location '{self.location}'..."
        ),
        success={
            "success": lambda self, env, name_value, location_value: (
                f"'Make' statement executed successfully for creating a new {self.entity_type} with name '{name_value}' and location '{location_value}'."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> None:
        try:
            name_value = self.name.execute(env)
            location_value = self.location.execute(env) if self.location else None
            path = os.path.join(location_value, name_value) if location_value else name_value
            if self.entity_type == "folder":
                if self.new:
                    os.makedirs(path, exist_ok=False)
                else:
                    os.makedirs(path, exist_ok=True)
            elif self.entity_type == "file":
                if self.new:
                    with open(path, "x") as f:
                        pass
                else:
                    with open(path, "a") as f:
                        pass
            
            log_case.set("success", name_value=name_value, location_value=location_value)
        except Exception as e:
            raise TraceError(node = self, cause = e)
        

  

@dataclass
class Delete(ASTNode):
    target: ASTNode
    def __post_init__(self):
        super().__init__()
    
    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking 'delete' statement with target '{self.target}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"'Delete' statement checked successfully with target '{self.target}'."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext , log_case: LogCase) -> None:
        try:
            self.child_return_types.clear()

            if self.target is None:
                raise Exception("Delete statement requires a target.")
            
            target_type = self.target.check(
                v_table=v_table, 
                f_table=f_table, 
                inference_context=inference_context
            )
            
            if not t_h.contains(target_type, "text"):
                raise Exception(f"Target in delete statement must be of type 'text', got '{target_type}'")
            
            
            if target_type != {"text"}:
                self.target.inference(
                    v_table=v_table,
                    f_table=f_table, 
                    inference_context=inference_context, 
                    old_inference_value=target_type, 
                    new_inference_value={"text"}
                )

                target_type = {"text"}

            self.child_return_types[self.target] = (target_type, self.target)
            log_case.set("success")


        except Exception as e:
            raise TraceError(node = self, cause = e)
        
    @logged(
        start=lambda self, env: (
            f"Executing 'delete' statement with target '{self.target}'..."
        ),
        success={
            "success": lambda self, env, target_value: (
                f"'Delete' statement executed successfully with target '{target_value}'."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> None:
        try:
            target_value = self.target.execute(env)
            if os.path.isdir(target_value):
                os.rmdir(target_value)
            elif os.path.isfile(target_value):
                os.remove(target_value)
            
            log_case.set("success", target_value=target_value)
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class Rename(ASTNode):
    target: ASTNode
    new_name: ASTNode
    def __post_init__(self):
        super().__init__()
    

    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking 'rename' statement to rename target '{self.target}' to new name '{self.new_name}'..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"'Rename' statement checked successfully'."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext , log_case: LogCase) -> None:
        try:
            self.child_return_types.clear()

            target_type = self.target.check(
                v_table=v_table, 
                f_table=f_table, 
                inference_context=inference_context
            )
            if not t_h.contains(target_type, "text"):
                raise Exception(f"Target in rename statement must be of type 'text', got '{target_type}'")

            if target_type != {"text"}:
                self.target.inference(
                    v_table=v_table,
                    f_table=f_table, 
                    inference_context=inference_context, 
                    old_inference_value=target_type, 
                    new_inference_value={"text"}
                )

                target_type = {"text"}

            self.child_return_types[self.target] = (target_type, self.target)


            new_name_type = self.new_name.check(
                v_table=v_table, 
                f_table=f_table, 
                inference_context=inference_context
            )
            if not t_h.contains(new_name_type, "text"):
                raise Exception(f"New name in rename statement must be of type 'text', got '{new_name_type}'")
            
            if new_name_type != {"text"}:
                self.new_name.inference(
                    v_table=v_table,
                    f_table=f_table, 
                    inference_context=inference_context, 
                    old_inference_value=new_name_type, 
                    new_inference_value={"text"}
                )

                new_name_type = {"text"}
            log_case.set("success")
            self.child_return_types[self.new_name] = (new_name_type, self.new_name)
        except Exception as e:
            raise TraceError(node = self, cause = e)
    

    @logged(
        start=lambda self, env: (
            f"Executing 'rename' statement'..."
        ),
        success={
            "success": lambda self, env, target_value, new_name_value: (
                f"'Rename' statement executed successfully for renaming target '{target_value}' to new name '{new_name_value}'."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> None:
        try:
            target_value = self.target.execute(env)
            new_name_value = self.new_name.execute(env)
            log_case.set("success", target_value=target_value, new_name_value=new_name_value)
            os.rename(target_value, new_name_value)
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class Copy(ASTNode):
    source: ASTNode
    target: ASTNode
    def __post_init__(self):
        super().__init__()
    

    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        try:
            self.child_return_types.clear()

            source_type = self.source.check(
                v_table=v_table, 
                f_table=f_table, 
                inference_context=inference_context
            )
            
            if not t_h.contains(source_type, "text"):
                raise Exception(f"Source in copy statement must be of type 'text', got '{source_type}'")
            

            if  source_type !=  {"text"}:
                self.source.inference(
                    v_table=v_table,
                    f_table=f_table, 
                    inference_context=inference_context, 
                    old_inference_value=source_type, 
                    new_inference_value={"text"}
                )

                source_type = {"text"}

            self.child_return_types[self.source] = (source_type, self.source)

            target_type = self.target.check(
                v_table=v_table, 
                f_table=f_table, 
                inference_context=inference_context
            )

            if not t_h.contains(target_type, "text"):
                raise Exception(f"Target in copy statement must be of type 'text', got '{target_type}'")
            
            narrowed_target_type = t_h.narrow(target_type, {"text"})
            if narrowed_target_type != target_type:
                self.target.inference(
                    v_table=v_table,
                    f_table=f_table, 
                    inference_context=inference_context,
                    old_inference_value=target_type, 
                    new_inference_value=narrowed_target_type
                )

                target_type = narrowed_target_type

            self.child_return_types[self.target] = (target_type, self.target)
        except Exception as e:
            raise TraceError(node = self, cause = e)
        
    def execute(self, env: Environment) -> None:
        try:
            source_value = self.source.execute(env)
            target_value = self.target.execute(env)
            if os.path.isdir(source_value):
                import shutil
                shutil.copytree(source_value, target_value)
            elif os.path.isfile(source_value):
                import shutil
                shutil.copy2(source_value, target_value)
        except Exception as e:
            raise TraceError(node = self, cause = e)
        

@dataclass
class Move(ASTNode):
    source: ASTNode
    target: ASTNode
    
    def __post_init__(self):
        super().__init__()

    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        try:
            self.child_return_types.clear()

            source_type = self.source.check(
                v_table=v_table, 
                f_table=f_table, 
                inference_context=inference_context
            )
            
            if not t_h.contains(source_type, "text"):
                raise Exception(f"Source in move statement must be of type 'text', got '{source_type}'")
            
            
            if source_type != {"text"}:
                self.source.inference(
                    v_table=v_table,
                    f_table=f_table, 
                    inference_context=inference_context, 
                    old_inference_value=source_type, 
                    new_inference_value={"text"}
                )

                source_type = {"text"}

            self.child_return_types[self.source] = (source_type, self.source)
            
            target_type = self.target.check(
                v_table=v_table, 
                f_table=f_table, 
                inference_context=inference_context
            )
            if not t_h.contains(target_type, "text"):
                raise Exception(f"Target in move statement must be of type 'text', got '{target_type}'")
            
            
            if target_type != {"text"}:
                self.target.inference(
                    v_table=v_table,
                    f_table=f_table, 
                    inference_context=inference_context, 
                    old_inference_value=target_type, 
                    new_inference_value={"text"}
                )

                target_type = {"text"}

            self.child_return_types[self.target] = (target_type, self.target)

        except Exception as e:
            raise TraceError(node = self, cause = e)
        
    def execute(self, env: Environment) -> None:
        try:
            source_value = self.source.execute(env)
            target_value = self.target.execute(env)
            os.rename(source_value, target_value)
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class Read(ASTNode):
    source: ASTNode
    def __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        try:
            self.child_return_types.clear()

            source_type = self.source.check(
                v_table=v_table, 
                f_table=f_table, 
                inference_context=inference_context
            )
            
            if not t_h.contains(source_type, "text"):
                raise Exception(f"Source in read statement must be of type 'text', got '{source_type}'")
            
            if source_type != {"text"}:
                self.source.inference(
                    v_table=v_table,
                    f_table=f_table, 
                    inference_context=inference_context, 
                    old_inference_value=source_type, 
                    new_inference_value={"text"}
                )

                source_type = {"text"}

                self.child_return_types[self.source] = (source_type, self.source)


        except Exception as e:
            raise TraceError(node = self, cause = e)
    
    def execute(self, env: Environment) -> str:
        try:
            source_value = self.source.execute(env)
            if os.path.isfile(source_value):
                with open(source_value, "r") as f:
                    return f.read()
            else:
                raise TraceError(node = self, cause = f"Cannot read from '{source_value}' because it is not a file.")
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class Write(ASTNode):
    target: ASTNode
    data: ASTNode
    
    def __post_init__(self):
        super().__init__()

    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None: 
        try:
            self.child_return_types.clear()

            target_type = self.target.check(
                v_table=v_table, 
                f_table=f_table, 
                inference_context=inference_context
            )
            if not t_h.contains(target_type, "text"):
                raise Exception(f"Target in write statement must be of type 'text', got '{target_type}'")
            if target_type != {"text"}:
                self.target.inference(
                    v_table=v_table,
                    f_table=f_table, 
                    inference_context=inference_context, 
                    old_inference_value=target_type, 
                    new_inference_value={"text"}
                )

                target_type = {"text"}

            self.child_return_types[self.target] = (target_type, self.target)

            data_type = self.data.check(
                v_table=v_table,
                f_table=f_table,
                inference_context=inference_context
            )
            if not t_h.contains(data_type, "text"):
                raise Exception(f"Data in write statement must be of type 'text', got '{data_type}'")
            if data_type != {"text"}:
                self.data.inference(
                    v_table=v_table,
                    f_table=f_table, 
                    inference_context=inference_context, 
                    old_inference_value=data_type, 
                    new_inference_value={"text"}
                )

                data_type = {"text"}
            self.child_return_types[self.data] = (data_type, self.data)

        except Exception as e:
            raise TraceError(node = self, cause = e)
        
    def execute(self, env: Environment) -> None:
        try:
            target_value = self.target.execute(env)
            data_value = self.data.execute(env)
            with open(target_value, "w") as f:
                f.write(data_value)
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class GoUp(ASTNode):
    

    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        return

    def execute(self, env: Environment) -> None:
        try:
            os.chdir("..")
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class Execute(ASTNode):
    target: ASTNode

    def __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        try:
            self.child_return_types.clear()

            target_type = self.target.check(
                v_table=v_table, 
                f_table=f_table, 
                inference_context=inference_context
            )

            if not t_h.contains(target_type, "text"):
                raise Exception(f"Target in execute statement must be of type 'text', got '{target_type}'")
            
            if target_type != {"text"}:
                self.target.inference(
                    v_table=v_table,
                    f_table=f_table, 
                    inference_context=inference_context, 
                    old_inference_value=target_type, 
                    new_inference_value={"text"}
                )

                target_type = {"text"}

            self.child_return_types[self.target] = (target_type, self.target)

        except Exception as e:
            raise TraceError(node = self, cause = e)
    
    def execute(self, env: Environment) -> None:
        try:
            target_value = self.target.execute(env)
            os.system(target_value)
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class Pause(ASTNode):
    


    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        return
    
    def execute(self, env: Environment) -> None:
        try:
            print("Press any key to continue...")
            msvcrt.getch()
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class Wait(ASTNode):
    time: ASTNode
    def __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> None:
        try:
            self.child_return_types.clear()
            duration_type = self.time.check(
                v_table=v_table, 
                f_table=f_table, 
                inference_context=inference_context
            )

            if not t_h.contains(duration_type, {"number", "decimal", "time"}):
                raise Exception(f"Duration in 'wait' statement must be of type 'number', 'decimal' or 'time', got '{duration_type}'")
            narrowed_duration_type = t_h.narrow(duration_type, {"number", "decimal", "time"})
            if narrowed_duration_type != duration_type:
                self.time.inference(
                    v_table=v_table,
                    f_table=f_table, 
                    inference_context=inference_context, 
                    old_inference_value=duration_type, 
                    new_inference_value=narrowed_duration_type
                )

                duration_type = narrowed_duration_type
            
            self.child_return_types[self.time] = (duration_type, self.time)

        except Exception as e:
            raise TraceError(node = self, cause = e)
        
    def execute(self, env: Environment) -> None:
        try:
            duration_value = self.time.execute(env)
            time.sleep(duration_value / 1000)
        except Exception as e:
            raise TraceError(node = self, cause = e)
        

@dataclass
class Input(ASTNode):
    prompt: Optional[ASTNode]

    def __post_init__(self):
        super().__init__()
    
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> Optional[str]:
        try:
            self.child_return_types.clear()
            if self.prompt is not None:
                prompt_type = self.prompt.check(v_table, f_table, inference_context)

                if not t_h.contains(prompt_type, "text"):
                    raise Exception(f"Prompt in input statement must be of type 'text', got '{prompt_type}'")
                
                if prompt_type != {"text"}:
                    self.prompt.inference(
                        v_table=v_table,
                        f_table=f_table, 
                        inference_context=inference_context, 
                        old_inference_value=prompt_type, 
                        new_inference_value={"text"}
                    )

                    prompt_type = {"text"}

                self.child_return_types["prompt"] = (prompt_type, self.prompt)
            self.child_return_types["self"] = ({"text"}, self)
            return {"text"}
        
        except Exception as e:
            raise TraceError(node = self, cause = e)
        
    def execute(self, env: Environment) -> str:
        try:
            prompt_value = self.prompt.execute(env) if self.prompt else ""
            return input(prompt_value)
        except Exception as e:
            raise TraceError(node = self, cause = e)