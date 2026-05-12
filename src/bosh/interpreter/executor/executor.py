from platform import node
from ..error_handler import BoshRuntimeError, RuntimeError
from .environment.environment import Environment
from bosh.abstract_syntax import *
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
            self.error_handler.report_error(
                message=e.message,
                error_type=RuntimeError,
                node=e.node
            )
        return None
