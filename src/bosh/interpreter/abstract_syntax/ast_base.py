from dataclasses import dataclass, field
from typing import List, Any, Optional
from ..semantics.symbol_table_scope_stacker import SymbolTableScopeStacker as ScopeStack
from ..semantics.func_table import FuncTable
from ..executor.environment.function_binding import FunctionBinding
from ..executor.environment.environment import Environment
from bosh.helper_functions.type_helper import UNKNOWN_TYPE, ANY_TYPE, EMPTY_LIST_TYPE, UNKNOWN_LIST_TYPE
import bosh.helper_functions.type_helper as t_h

@dataclass
class Position():
    line: Optional[int] = None
    start_col: Optional[int] = None
    end_col: Optional[int] = None
    filename: Optional[str] = None

@dataclass
class InferenceContext:
    def __init__(self):
        self.__changed: bool = False

    def has_changed(self) -> bool:
        return self.__changed
    
    def mark_infered(self):
        self.__changed = True

    def reset(self):
        self.__changed = False

    def load_state(self, other: "InferenceContext"):
        self.__changed = other.__changed
    
    def save_state(self) -> "InferenceContext":
        new_context = InferenceContext()
        new_context.__changed = self.__changed
        return new_context

class ASTNode():
    pos: Optional[Position] = None
    def __init__(self):
        """
        child_return_types is a dictionary that maps a string key to a tuple of a set of strings and an ASTNode.
        The string key is used to identify the child node, the set of strings is used to remember the return type of that child node,
        and the ASTNode is used to reference the child node itself for inference purposes. This allows us to update the remembered return type for a child node during inference when we encounter a situation where we can narrow the type of a variable based on new information.
        it can also be used to get the types in Execution.
        """
        self.child_return_types: dict[str, tuple[set[str], "ASTNode"]] = {}

    def set_meta(self, meta, filename: Optional[str] = None):
        if meta is not None:
            self.pos = Position(
                line=meta.line,
                start_col=meta.column,
                end_col=meta.end_column,
                filename=filename
            )

    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> Optional[set[str]]:
        raise NotImplementedError(self.__class__.__name__ + " does not implement check()")
    
    def execute(self, env: Environment) -> Any:
        raise NotImplementedError(self.__class__.__name__ + " does not implement execute()")
    
    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                inference_context: InferenceContext,
                old_inference_value: set[str],
                new_inference_value: set[str]) -> None:
        try:
            raise NotImplementedError(self.__class__.__name__ + " has not just implemented inference(), but it is needed for inference. This error is raised to indicate that this node needs to implement inference() in order to be used in inference, and to provide a clear error message if it is not implemented.")
        except Exception as e:
            raise TraceError(node = self, cause = e)
        
            


@dataclass
class Block(ASTNode):
    statements: List[ASTNode]

    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext) -> Optional[set[str]]:
        vvvprint(f"Block: Checking block with {len(self.statements)} statements...")
        return_type = None
        for stmt in self.statements:
            vvvprint(f"Block: Checking statement {stmt}...")
            stmt_return_type = stmt.check(v_table, f_table, inference_context)
            vvvprint(f"Block: Finished checking statement {stmt} with return type: {stmt_return_type}")
            if stmt_return_type is not None:
                vvvprint(f"Block: Statement {stmt} has return type: {stmt_return_type}")
                if return_type is not None and stmt_return_type != return_type:
                    raise TraceError(node = self, cause = f"All statements in a block must return the same type, but got '{return_type}' and '{stmt_return_type}'")
                vvvprint(f"Block: Setting block return type to: {stmt_return_type}")
                return_type = stmt_return_type
        return return_type

    def execute(self, env: Environment) -> Any:
        vvvprint(f"Block: Executing block with {len(self.statements)} statements...")
        for stmt in self.statements:
            vvvprint(f"Block: Executing statement {stmt}...")
            return_val = stmt.execute(env)
            vvvprint(f"Block: Finished executing statement {stmt} with return value: {return_val}")
            if return_val is not None:
                vvvprint(f"Block: Statement {stmt} returned value: {return_val}, exiting block execution.")
                return return_val
            
    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                inference_context: InferenceContext,
                old_inference_value: set[str],
                new_inference_value: set[str]) -> None:
        vvvprint(f"Block: does not implement inference, but checking if any child nodes need to be updated with new inference value '{new_inference_value}'...")
        

@dataclass
class Program(ASTNode):
    block: Block
    def __post_init__(self):
        super().__init__()

    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[set[str]]:
        try:
            self.child_return_types.clear()
            vvvprint("Program: Starting type checking of program...")

            inference_context = InferenceContext()
            return_value = None
            
            while True:
                inference_context.reset()
                vvvprint("Program: Starting a new inference iteration...")

                return_value = self.block.check(
                    v_table=v_table,
                    f_table=f_table,
                    inference_context=inference_context
                )

                if not inference_context.has_changed():
                    vvvprint("Program: No changes in inference, finished type checking.")
                    break

                vvvprint("Program: Changes detected in inference, starting another iteration...")

            return return_value
        
        except Exception as e:
            raise TraceError(node = self, cause = e)

    def execute(self, env: Environment) -> Any:
        vvvprint("Program: Starting execution of program...")
        return self.block.execute(env)
    
    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                inference_context: InferenceContext,
                old_inference_value: set[str],
                new_inference_value: set[str]) -> None:
         raise Exception(f"Program: does not implement inference, but checking if any child nodes need to be updated with new inference value '{new_inference_value}'...")