# app imports
import builtins

# Errors
from bosh.app.error_handler.errors import RunTypeError, ArgumentError, CLIError, ConfigurationError, BoshTypeError, BoshRuntimeError

# helper function imports
from bosh.helper_functions.print import print_error, vprint, vvprint, vvvprint, indent
from bosh.helper_functions.get import get_code, get_line


class GlobalImporter:
    def import_all(self):
        self.import_errors()
        self.import_helper()

    def import_errors(self):
        builtins.RunTypeError = RunTypeError
        builtins.ArgumentError = ArgumentError
        builtins.CLIError = CLIError
        builtins.ConfigurationError = ConfigurationError
        builtins.BoshTypeError = BoshTypeError
        builtins.BoshRuntimeError = BoshRuntimeError

    def import_helper(self):
        builtins.print_error = print_error
        builtins.vprint = vprint
        builtins.vvprint = vvprint
        builtins.vvvprint = vvvprint
        builtins.indent = indent
        builtins.get_code = get_code
        builtins.get_line = get_line