
from .table import Table
from .function_binding import FunctionBinding

# made for logging purposes, to get "FunctionTable:" not "Table:" in logs
class FunctionTable(Table[FunctionBinding]):
    pass