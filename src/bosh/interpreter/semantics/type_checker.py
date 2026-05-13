from typing import Any, Optional
from .func_table import FuncTable, FunctionSignature
from ..abstract_syntax import *
from .symbol_table_scope_stacker import SymbolTableScopeStacker

class TypeChecker:
    from ..abstract_syntax import Program
    def __init__(self):
        self.v_table = SymbolTableScopeStacker()
        self.f_table = FuncTable()

    def check(self, program_ast: Program):
        try:
            program_ast.check(self.v_table, self.f_table)
        except BoshTypeError as e:
            pass