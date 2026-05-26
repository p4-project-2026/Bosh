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
            f"Checking 'go to' statement..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"'Go to' statement checked successfully with path type '{self.child_return_types['path'][0]}'."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> None:
        try:
            self.child_return_types.clear()

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
            
            self.child_return_types["path"] = (path_type, self.path)
            log_case.set("success")

        except Exception as e:
            raise TraceError(node = self, cause = e)
    
    @logged(
        start=lambda self, env: (
            f"Executing 'go to' statement with..."
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
            if os.path.isabs(path_value):
                if not os.path.exists(path_value):
                    raise TraceError(node = self, cause = f"Path '{path_value}' does not exist.")
            else:
                path_value = os.path.join(env.get_current_directory(), path_value)
                if not os.path.exists(path_value):
                    raise TraceError(node = self, cause = f"Path '{path_value}' does not exist.")
            
            env.set_current_directory(path_value)
            log_case.set("success", path_value=path_value)
        except Exception as e:
            raise TraceError(node = self, cause = e)
        return
        


@dataclass
class Make(ASTNode):
    new: bool
    entity_type: str
    name: ASTNode
    location: Optional[ASTNode]
    def __post_init__(self):
        super().__init__()
    

    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking 'make' statement to create a new {self.entity_type}..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"'Make' statement checked successfully for creating a new {self.entity_type}."
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
                
            self.child_return_types["name"] = (name_type, self.name)
            if self.location is not None:
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
                    self.child_return_types["location"] = (location_type, self.location)
                
                else:
                    location_type = {"text"}
                    self.child_return_types["location"] = (location_type, None)
                
            

            
            log_case.set("success")

        except Exception as e:
            raise TraceError(node = self, cause = e)


    @logged(
        start=lambda self, env: (
            f"Executing 'make' statement to create a new {self.entity_type}..."
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
            if self.location is not None:
                location_value = self.location.execute(env)

            else:
                location_value = env.get_current_directory()

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
                f"'Delete' statement checked successfully with target '{self.child_return_types['target'][1]}'."
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

            self.child_return_types["target"] = (target_type, self.target)
            log_case.set("success")


        except Exception as e:
            raise TraceError(node = self, cause = e)
        
    @logged(
        start=lambda self, env: (
            f"Executing 'delete' statement'..."
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
            f"Checking 'rename' statement..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"'Rename' statement checked successfully. Target: '{self.child_return_types['target'][1]}', New Name: '{self.child_return_types['new_name'][1]}'"
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

            self.child_return_types["target"] = (target_type, self.target)


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
            self.child_return_types["new_name"] = (new_name_type, self.new_name)
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
    

    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking 'copy' statement..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
            f"'Copy' statement checked successfully'."
            )
        }
    )
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

            self.child_return_types["source"] = (source_type, self.source)

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

            self.child_return_types["target"] = (target_type, self.target)
        except Exception as e:
            raise TraceError(node = self, cause = e)
        
    
    @logged(
        start=lambda self, env: (
            f"Executing 'copy' statement..."
        ),
        success={
            "success": lambda self, env, source_value, target_value: (
                f"'Copy' statement executed successfully. Copied from '{source_value}' to '{target_value}'"
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> None:
        try:
            source_value = self.source.execute(env)
            target_value = self.target.execute(env)
            if os.path.isdir(source_value):
                import shutil
                shutil.copytree(source_value, target_value)
            elif os.path.isfile(source_value):
                import shutil
                shutil.copy2(source_value, target_value)

            log_case.set("success", source_value=source_value, target_value=target_value)
        except Exception as e:
            raise TraceError(node = self, cause = e)
        

@dataclass
class Move(ASTNode):
    source: ASTNode
    target: ASTNode
    
    def __post_init__(self):
        super().__init__()


    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking 'move' statement..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"'Move' statement checked successfully. Source: {self.child_return_types['source']}, Target: {self.child_return_types['target']}"
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> None:
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

            self.child_return_types["source"] = (source_type, self.source)
            
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

            self.child_return_types["target"] = (target_type, self.target)
            log_case.set("success")

        except Exception as e:
            raise TraceError(node = self, cause = e)
        
    @logged(
        start=lambda self, env: (
            f"Executing 'move' statement..."
        ),
        success={
            "success": lambda self, env, source_value, target_value: (
                    f"'Move' statement executed successfully. Moved from '{source_value}' to '{target_value}'"
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> None:
        try:
            source_value = self.source.execute(env)
            target_value = self.target.execute(env)
            os.rename(source_value, target_value)
            log_case.set("success", source_value=source_value, target_value=target_value)
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class Read(ASTNode):
    source: ASTNode
    def __post_init__(self):
        super().__init__()
    
    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking 'read' statement..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"'Read' statement checked successfully."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> None:
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

                self.child_return_types["source"] = (source_type, self.source)
            
            log_case.set("success")

        except Exception as e:
            raise TraceError(node = self, cause = e)

    @logged(
        start=lambda self, env: (
            f"Executing 'read' statement..."
        ),
        success={
            "success": lambda self, env, source_value: (
                f"'Read' statement executed successfully with source '{source_value}'."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> str:
        try:
            source_value = self.source.execute(env)
            if os.path.isfile(source_value):
                with open(source_value, "r") as f:
                    log_case.set("success", source_value=source_value)
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
    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking 'write' statement..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"'Write' statement checked successfully. Target: {self.child_return_types['target']}, Data: {self.child_return_types['data']}"
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> None: 
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

            self.child_return_types["target"] = (target_type, self.target)

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
            self.child_return_types["data"] = (data_type, self.data)
            log_case.set("success")

        except Exception as e:
            raise TraceError(node = self, cause = e)
    
    @logged(
        start=lambda self, env: (
            f"Executing 'write' statement..."
        ),
        success={
            "success": lambda self, env, target_value, data_value: (
                f"'Write' statement executed successfully for writing data '{data_value}' to target '{target_value}'."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> None:
        try:
            target_value = self.target.execute(env)
            data_value = self.data.execute(env)
            with open(target_value, "w") as f:
                f.write(data_value)
            log_case.set("success", target_value=target_value, data_value=data_value)
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class GoUp(ASTNode):
    
    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking 'go up' statement..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"'Go up' statement checked successfully'."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> None:
        log_case.set("success")
        return


    @logged(
        start=lambda self, env: (
            f"Executing 'go up' statement..."
        ),
        success={
            "success": lambda self, env, old_directory, new_directory: (
                f"'Go up' statement executed successfully, current directory changed from '{old_directory}' to its parent directory '{new_directory}'."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> None:
        try:
            current_dir = env.get_current_directory()
            new_current_dir = current_dir[:current_dir.rfind('/')+1]
            env.set_current_directory(new_current_dir)
            log_case.set("success", old_directory=current_dir, new_directory=new_current_dir)
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class Execute(ASTNode):
    target: ASTNode

    def __post_init__(self):
        super().__init__()
    

    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking 'execute' statement..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"'Execute' statement checked successfully. Target: {self.child_return_types['target'][0]}"
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> None:
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

            self.child_return_types["target"] = (target_type, self.target)
            log_case.set("success")

        except Exception as e:
            raise TraceError(node = self, cause = e)
    

    @logged(
        start=lambda self, env: (
            f"Executing 'execute' statement..."
        ),
        success={
            "success": lambda self, env, target_value: (
                f"'Execute' statement executed successfully with target '{target_value}'."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> None:
        try:
            target_value = self.target.execute(env)

            os.system(target_value)
            log_case.set("success", target_value=target_value)
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class Pause(ASTNode):
    

    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking 'pause' statement..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"'Pause' statement checked successfully'."
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> None:
        log_case.set("success")
        return
    

    @logged(
        start=lambda self, env: (
            f"Executing 'pause' statement..."
        ),
        success={
            "success": lambda self, env: (
                f"'Pause' statement executed successfully, execution paused until user input."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> None:
        try:
            print("Press any key to continue...")
            msvcrt.getch()
            log_case.set("success")
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class Wait(ASTNode):
    time: ASTNode
    def __post_init__(self):
        super().__init__()
    

    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking 'wait' statement..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"'Wait' statement checked successfully. Duration type: {self.child_return_types['time'][0]}"
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> None:
        try:
            self.child_return_types.clear()
            duration_type = self.time.check(
                v_table=v_table, 
                f_table=f_table, 
                inference_context=inference_context
            )
            
            if not t_h.is_compatible(duration_type, {"number", "decimal", "time"}):
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
            
            self.child_return_types["time"] = (duration_type, self.time)
            log_case.set("success")


        except Exception as e:
            raise TraceError(node = self, cause = e)
        
    @logged(
        start=lambda self, env: (
            f"Executing 'wait' statement..."
        ),
        success={
            "success": lambda self, env, duration_value: (
                f"'Wait' statement executed successfully, execution paused for {duration_value} milliseconds."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> None:
        try:
            duration_value = self.time.execute(env)
            time.sleep(duration_value / 1000)
            log_case.set("success", duration_value=duration_value)
        except Exception as e:
            raise TraceError(node = self, cause = e)
        

@dataclass
class Input(ASTNode):
    prompt: Optional[ASTNode]

    def __post_init__(self):
        super().__init__()
    

    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking 'input' statement..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context: (
                f"'Input' statement checked successfully. Prompt type: {self.child_return_types['prompt'][0] if self.prompt else 'None'}, Return type: {self.child_return_types['self'][0]}"
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> set[str]:
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
        
    @logged(
        start=lambda self, env: (
            f"Executing 'input' statement..."
        ),
        success={
            "success": lambda self, env, prompt_value: (
                f"'Input' statement executed successfully with prompt '{prompt_value}'."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> str:
        try:
            prompt_value = self.prompt.execute(env) if self.prompt else ""
            log_case.set("success", prompt_value=prompt_value)
            return input(prompt_value)
        except Exception as e:
            raise TraceError(node = self, cause = e)