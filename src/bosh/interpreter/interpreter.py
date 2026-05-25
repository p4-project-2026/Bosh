from bosh.app.cli.arguments.argument_handler import ArgumentHandler
from bosh.helper_functions.print import indent, vprint, vvprint
from bosh.interpreter.pre_processor.pre_processor import PreProcessor
from bosh.interpreter.lexparser.parser import parseBosh, createAST
from bosh.interpreter.semantics.type_checker import TypeChecker
from bosh.interpreter.executor.executor import Executor

from bosh.app.cli.flags.flags import Cmd
class Interpreter:
    code = None
    processed_code = None
    parse_tree = None
    ast = None

    def initializer(self, file_path):
        vprint(f"Running {file_path} with Cmd: {Cmd.enabled}")

        if Cmd.enabled:
            self._run_cmd()
            return

        # open and load the file
        vprint(f"Opening file: {file_path}...")
        try:
            Interpreter.code = self._load_code_from_file(file_path)
        except FileNotFoundError as e:
            raise BoshFileNotFoundError(f"File not found: {file_path}")
        vvprint(indent(Interpreter.code))

        self.run()

    def _run_cmd(self):
        for i, code in enumerate(ArgumentHandler.args):
            vprint(f"Running argument {i + 1}: ")
            Interpreter.code = code
            self.run()

    def run(self):
        # Preprocess the code
        vprint("Preprocessing code...")
        Interpreter.processed_code = PreProcessor().run(Interpreter.code)
        vvprint(indent(Interpreter.processed_code))

        vprint("Creating parse-tree...")
        Interpreter.parse_tree = parseBosh(Interpreter.processed_code)
        vvprint(indent(Interpreter.parse_tree.pretty()))

        vprint("Building AST...")
        Interpreter.ast = createAST(Interpreter.parse_tree)
        vvprint(indent(Interpreter.ast))

        vprint("Type checking...")
        TypeChecker().check(Interpreter.ast)
        vvprint(indent("Type checking passed!"))

        vprint("Executing code...\n")
        vprint("Output:")
        Executor().execute(Interpreter.ast)
        vvprint("\nExecution complete")


    def _load_code_from_file(self, file_path):
        with open(file_path, "r") as f:
            code = f.read()
            return code
