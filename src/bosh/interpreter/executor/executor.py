from platform import node
from app.error_handler.errors import BoshRuntimeError
from .environment.environment import Environment
from interpreter.abstract_syntax import *

class Executor:
    # __init__
    def __init__(self):
        self.environment = Environment()

    # evaluate
    def execute(self, node: Program):
        try:
            # node.execute(self.environment)
            pass
        except BoshRuntimeError as e:
            pass