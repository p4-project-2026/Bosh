from platform import node
from .environment.environment import Environment
from ..abstract_syntax import *

class Executor:
    # __init__
    def __init__(self):
        self.environment = Environment()

    # evaluate
    def execute(self, node: Program):
        vvvprint("Executor: Starting execution of the program...")
        #node.execute(self.environment)
        vvvprint("Executor: Program execution completed.")