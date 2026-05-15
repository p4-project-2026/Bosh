import msvcrt
from .ast_base import *
import os
import time

@dataclass
class GoTo(ASTNode):
    path: ASTNode

    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        try:
            path_type = self.path.check(v_table, f_table)
            if path_type != "text":
                raise TraceError(node = self, cause = f"Path in 'go to' statement must be of type 'text', got '{path_type}'")
        except Exception as e:
            raise TraceError(node = self, cause = e)
    
    def execute(self, env: Environment) -> None:
        try:
            path_value = self.path.execute(env)
            os.chdir(path_value)
        except Exception as e:
            raise TraceError(node = self, cause = e)

@dataclass
class Make(ASTNode):
    new: bool
    entity_type: str
    name: ASTNode
    location: ASTNode
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        try:
            if self.entity_type not in ["folder", "file"]:
                raise TraceError(node = self, cause = f"Entity type in make statement must be 'folder' or 'file', got '{self.entity_type}'")

            location_type = self.location.check(v_table, f_table) if self.location else "text"
            
            if location_type != "text":
                raise TraceError(node = self, cause = f"Path in make statement must be of type 'text', got '{location_type}'")

            name_type = self.name.check(v_table, f_table)
            if name_type is not None and name_type != "text":
                raise TraceError(node = self, cause = f"Cannot use type '{name_type}' as a new name. Expected 'text'.")
        except Exception as e:
            raise TraceError(node = self, cause = e)

    def execute(self, env: Environment) -> None:
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
        except Exception as e:
            raise TraceError(node = self, cause = e)
        

@dataclass
class Delete(ASTNode):
    target: ASTNode
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        try:
            target_type = self.target.check(v_table, f_table)
            if target_type != "text":
                raise TraceError(node = self, cause = f"Cannot delete type '{target_type}'. Expected 'text'.")
        except Exception as e:
            raise TraceError(node = self, cause = e)
        
    def execute(self, env: Environment) -> None:
        try:
            target_value = self.target.execute(env)
            if os.path.isdir(target_value):
                os.rmdir(target_value)
            elif os.path.isfile(target_value):
                os.remove(target_value)
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class Rename(ASTNode):
    target: ASTNode
    new_name: ASTNode
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        try:
            target_type = self.target.check(v_table, f_table)
            new_name_type = self.new_name.check(v_table, f_table)
            if target_type != "text":
                raise TraceError(node = self, cause = f"Cannot rename type '{target_type}'. Expected 'text'.")
            if new_name_type != "text":
                raise TraceError(node = self, cause = f"New name must be of type 'text', got '{new_name_type}'")
        except Exception as e:
            raise TraceError(node = self, cause = e)
    
    def execute(self, env: Environment) -> None:
        try:
            target_value = self.target.execute(env)
            new_name_value = self.new_name.execute(env)
            os.rename(target_value, new_name_value)
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class Copy(ASTNode):
    source: ASTNode
    target: ASTNode
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        try:
            source_type = self.source.check(v_table, f_table)
            target_type = self.target.check(v_table, f_table)
            if source_type != "text":
                raise TraceError(node = self, cause = f"Cannot copy type '{source_type}'. Expected 'text'.")
            if target_type != "text":
                raise TraceError(node = self, cause = f"Target location in copy statement must be of type 'text', got '{target_type}'")
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
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        try:
            source_type = self.source.check(v_table, f_table)
            target_type = self.target.check(v_table, f_table)
            if source_type != "text":
                raise TraceError(node = self, cause = f"Cannot move type '{source_type}'. Expected 'text'.")
            if target_type != "text":
                raise TraceError(node = self, cause = f"Target location in move statement must be of type 'text', got '{target_type}'")
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
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        try:
            source_type = self.source.check(v_table, f_table)
            if source_type != "text":
                raise TraceError(node = self, cause = f"Cannot read type '{source_type}'. Expected 'text'.")
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
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None: 
        try:
            target_type = self.target.check(v_table, f_table)
            data_type = self.data.check(v_table, f_table)
            if target_type != "text":
                raise TraceError(node = self, cause = f"Cannot write to type '{target_type}'. Expected 'text'.")
            if data_type != "text":
                raise TraceError(node = self, cause = f"Data in write statement must be of type 'text', got '{data_type}'")
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
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        return

    def execute(self, env: Environment) -> None:
        try:
            os.chdir("..")
        except Exception as e:
            raise TraceError(node = self, cause = e)


@dataclass
class Execute(ASTNode):
    target: ASTNode
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        try:
            target_type = self.target.check(v_table, f_table)
            if target_type != "text":
                raise TraceError(node = self, cause = f"Cannot execute type '{target_type}'. Expected 'text'.")
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
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
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
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        try:
            duration_type = self.time.check(v_table, f_table)
            if duration_type not in ["number", "decimal", "time"]:
                raise TraceError(node = self, cause = f"Duration in 'wait' must be of type 'number', 'decimal' or 'time', got '{duration_type}'")
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
    
    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[str]:
        try:
            prompt_type = self.prompt.check(v_table, f_table) if self.prompt else None
            if prompt_type != "text" and prompt_type is not None:
                raise TraceError(node = self, cause = f"Prompt in input statement must be of type 'text', got '{prompt_type}'")
            return "text"
        except Exception as e:
            raise TraceError(node = self, cause = e)
        
    def execute(self, env: Environment) -> str:
        try:
            prompt_value = self.prompt.execute(env) if self.prompt else ""
            return input(prompt_value)
        except Exception as e:
            raise TraceError(node = self, cause = e)