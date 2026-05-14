from dataclasses import dataclass
from typing import List, Any, Optional
from ..semantics.symbol_table_scope_stacker import SymbolTableScopeStacker as ScopeStack
from ..semantics.func_table import FuncTable
from ..executor.environment.function_binding import FunctionBinding
from ..executor.environment.environment import Environment

@dataclass
class Position():
    line: Optional[int] = None
    start_col: Optional[int] = None
    end_col: Optional[int] = None
    filename: Optional[str] = None


class ASTNode():
    pos: Optional[Position] = None

    def set_meta(self, meta, filename: Optional[str] = None):
        if meta is not None:
            self.pos = Position(
                line=meta.line,
                start_col=meta.column,
                end_col=meta.end_column,
                filename=filename
            )

    def check(self, v_table: ScopeStack, f_table: FuncTable) -> None:
        raise NotImplementedError(self.__class__.__name__ + " does not implement check()")
    
    def execute(self, env: Environment) -> Any:
        raise NotImplementedError(self.__class__.__name__ + " does not implement execute()")


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
                    raise LocationError(node = self, cause = f"All statements in a block must return the same type, but got '{return_type}' and '{stmt_return_type}'")
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