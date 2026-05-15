from bosh.app.cli.arguments.argument_handler import ArgumentHandler
from bosh.helper_functions.print import indent, vprint, vvprint
from bosh.interpreter.pre_processor.pre_processor import PreProcessor
from bosh.interpreter.lexparser.parser import parseBosh, createAST
from bosh.interpreter.semantics.type_checker import TypeChecker
from bosh.interpreter.executor.executor import Executor

class Interpreter:
    code = None
    processed_code = None
    parse_tree = None
    ast = None

    def initializer(self, file_path, run_type):
        vprint(f"Running {file_path} with run type: {run_type}")
        if run_type == "cli":
            self._run_cli()
            return

        if run_type == "cmd":
            self._run_cmd()
            return

        # open and load the file
        vprint(f"Opening file: {file_path}...")
        Interpreter.code = self._load_code_from_file(file_path)
        vvprint(indent(Interpreter.code))

        self.run()

    def _run_cmd(self):
        for i, code in enumerate(ArgumentHandler.args):
            vprint(f"Running argument {i + 1}: ")
            Interpreter.code = code
            self.run()

    def _run_cli(self):
        print("Welcome to Bosh CLI IDE!")
        print("Type your code below. Type 'exit' to quit.")
        while True:
            try:
                code = input(">>> ")
                if code.strip() == "exit":
                    print("Goodbye!")
                    break
                # Here you would normally pass the code to your interpreter logic
                # TODO: Implement the actual code execution logic
                print(f"You entered: {code}")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break

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
