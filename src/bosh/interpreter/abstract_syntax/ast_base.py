from dataclasses import dataclass, field
from typing import List, Any, Optional
from ..semantics.symbol_table_scope_stacker import SymbolTableScopeStacker as ScopeStack
from ..semantics.func_table import FuncTable
from ..executor.environment.function_binding import FunctionBinding
from ..executor.environment.environment import Environment
from bosh.app.error_handler.errors import BoshTypeError, BoshRuntimeError

@dataclass
class Position():
    line: Optional[int] = None
    start_col: Optional[int] = None
    end_col: Optional[int] = None
    filename: Optional[str] = None


class ASTNode():
    pos: Optional[Position] = None
    def __init__(self):
        self.value_node_pairs: list[tuple[set[str], "ASTNode"]] = []

    def set_meta(self, meta, filename: Optional[str] = None):
        if meta is not None:
            self.pos = Position(
                line=meta.line,
                start_col=meta.column,
                end_col=meta.end_column,
                filename=filename
            )

    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        raise BoshTypeError(self.__class__.__name__ + " does not implement check()", self)
    
    def execute(self, env: Environment) -> Any:
        raise NotImplementedError(self.__class__.__name__ + " does not implement execute()")
    
    def inference(self,
                v_table: ScopeStack,
                f_table: FuncTable,
                old_inference_value: set[str],
                new_inference_value: set[str]) -> None:
        new_list = []
        for value, node in self.value_node_pairs:
            # i want to check if all the values in inference_value are in value and vice versa, and if so, run inference on the node with new_inference_value then replace value with new_inference_value and check the next one
            if old_inference_value == value:
                node.inference(v_table, f_table, old_inference_value, new_inference_value)
                new_list.append((new_inference_value.copy(), node))
            else:
                new_list.append((value, node))
        self.value_node_pairs = new_list

        
            


@dataclass
class Block(ASTNode):
    statements: List[ASTNode]

    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[str]:
        vvvprint(f"Block: Checking block with {len(self.statements)} statements...")
        return_type = None
        for stmt in self.statements:
            vvvprint(f"Block: Checking statement {stmt}...")
            stmt_return_type = stmt.check(v_table, f_table)
            vvvprint(f"Block: Finished checking statement {stmt} with return type: {stmt_return_type}")
            if stmt_return_type is not None:
                vvvprint(f"Block: Statement {stmt} has return type: {stmt_return_type}")
                if return_type is not None and stmt_return_type != return_type:
                    raise BoshTypeError(f"All statements in a block must return the same type, but got '{return_type}' and '{stmt_return_type}'", self)
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

@dataclass
class Program(ASTNode):
    block: Block

    def check(self, v_table: ScopeStack, f_table: FuncTable) -> Optional[str]:
        vvvprint("Program: Starting type checking of program...")
        return self.block.check(v_table, f_table)
        vvvprint("Program: Finished type checking of program.")
    
    def execute(self, env: Environment) -> Any:
        vvvprint("Program: Starting execution of program...")
        return self.block.execute(env)
        vvvprint("Program: Finished execution of program.")