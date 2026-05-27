from dataclasses import dataclass, field
from typing import List, Any, Optional, Literal
from ..semantics.symbol_table_scope_stacker import SymbolTableScopeStacker as ScopeStack
from ..semantics.func_table import FuncTable
from ..executor.environment.function_binding import FunctionBinding
from ..executor.environment.environment import Environment
from bosh.helper_functions.type_helper import UNKNOWN_TYPE, ANY_TYPE, EMPTY_LIST_TYPE, UNKNOWN_LIST_TYPE
import bosh.helper_functions.type_helper as t_h
import bosh.helper_functions.formating as f_h
from bosh.helper_functions.logged import logged, LogCase

ExecutionSignal = Literal["continue", "break"]

@dataclass
class Position():
    line: Optional[int] = None
    start_col: Optional[int] = None
    end_col: Optional[int] = None
    filename: Optional[str] = None


class InferenceContext:
    def __init__(self):
        self.__changed: bool = False

    def has_changed(self) -> bool:
        return self.__changed
    
    def mark_inferred(self):
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
        
        raise Exception(
            self.__class__.__name__ + f" does not implement inference() but was called during inference. " 
            f"This means there is likely a bug in the inference pathing logic, or the node is missing a proper inference implementation." 
            f"Node: {self}, old_inference_value: {old_inference_value}, new_inference_value: {new_inference_value}"
        )

        
            


@dataclass
class Block(ASTNode):
    statements: List[ASTNode]

    @logged(
        start=lambda self, v_table, f_table, inference_context: (
            f"Checking block with statements..."
        ),
        success={
            "success": lambda self, v_table, f_table, inference_context, return_type: (
                f"Block checked successfully with return type: {return_type}"
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, inference_context: InferenceContext, log_case: LogCase) -> Optional[set[str]]:
        return_type = None
        for stmt in self.statements:
            stmt_return_type = stmt.check(v_table, f_table, inference_context)
            if stmt_return_type is None:
                continue
            
            if return_type is None:
                return_type = stmt_return_type
                continue

            if not t_h.is_compatible(return_type, stmt_return_type):
                raise Exception(f"Type error: Incompatible return types in block. Previous return type: {return_type}, new return type: {stmt_return_type}")
                    
            return_type = t_h.narrow(return_type, stmt_return_type)
                
        log_case.set("success", return_type=return_type)
        return return_type

    @logged(
        start=lambda self, env: (
            f"Executing block with statements..."
        ),
        success={
            "return_val": lambda self, env, return_val: (
                f"Block executed successfully with return value: {return_val}"
            ),
            "no_return": lambda self, env: (
                f"Block executed successfully with no return value."
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> Any:
        for stmt in self.statements:
            return_val = stmt.execute(env)
            if return_val is not None:
                log_case.set("return_val", return_val=return_val)
                return return_val
        log_case.set("no_return")
            
            

        

@dataclass
class Program(ASTNode):
    block: Block
    def __post_init__(self):
        super().__init__()

    @logged(
        start=lambda self, v_table, f_table: (
            f"Starting type checking of the program..."
        ),
        success={
            "success": lambda self, v_table, f_table, return_type: (
                f"Program type checked successfully with return type: {return_type}"
            )
        }
    )
    def check(self, v_table: ScopeStack, f_table: FuncTable, log_case: LogCase) -> Optional[set[str]]:
        try:
            self.child_return_types.clear()
            inference_context = InferenceContext()
            return_value = None
            
            while True:
                inference_context.reset()
                return_value = self.block.check(
                    v_table=v_table,
                    f_table=f_table,
                    inference_context=inference_context
                )

                if not inference_context.has_changed():
                    break

                vvvprint("Program: Detected a change during inference, restarting type checking with updated types...")

            log_case.set("success", return_type=return_value)
            return return_value
        
        except Exception as e:
            raise TraceError(node = self, cause = e)

    @logged(
        start=lambda self, env: (
            f"Starting execution of program..."
        ),
        success={
            "return_val": lambda self, env, return_val: (
                f"Program executed successfully with return value: {return_val}"
            )
        }
    )
    def execute(self, env: Environment, log_case: LogCase) -> Any:
        return_val = self.block.execute(env)
        log_case.set("return_val", return_val=return_val)
        return return_val
    
