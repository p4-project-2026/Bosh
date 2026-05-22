from typing import Any, Optional
from .func_table import FuncTable, FunctionSignature
from ..abstract_syntax import *
from .symbol_table_scope_stacker import SymbolTableScopeStacker
from bosh.helper_functions.logged import logged, LogCase

class TypeChecker:
    from ..abstract_syntax import Program
    def __init__(self):
        self.v_table = SymbolTableScopeStacker()
        self.f_table = FuncTable()

    @logged(
        start=lambda self, program_ast: (
            f"Starting type checking of the program..."
        ),
        success={"success":
            lambda self, program_ast: (
                f"Program type checked successfully with no type errors."
            )
        }
    )
    def check(self, program_ast: Program, log_case: LogCase):
        program_ast.check(self.v_table, self.f_table)
        log_case.set("success")
