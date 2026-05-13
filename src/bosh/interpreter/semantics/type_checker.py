from typing import Any, Optional
from bosh.interpreter.abstract_syntax import *
from app.error_handler.errors import BoshTypeError
from .func_table import FuncTable, FunctionSignature
from .symbol_table_scope_stacker import SymbolTableScopeStacker

class TypeChecker:
    def __init__(self):
        self.v_table = SymbolTableScopeStacker()
        self.f_table = FuncTable()

    def check(self, program_ast: Program):
        try:
            program_ast.check(self.v_table, self.f_table)
        except BoshTypeError as e:
            pass