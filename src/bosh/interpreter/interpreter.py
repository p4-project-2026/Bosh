from bosh.app.cli.arguments.argument_handler import ArgumentHandler
from bosh.helper_functions.print import indent, vprint, vvprint
from bosh.interpreter.pre_processor.pre_processor import PreProcessor
class Interpreter:
    code = None

    def run(self, file_path, run_type):
        vprint(f"Running {file_path} with run type: {run_type}")

        if run_type == "err":
            print("run type: err. this error should never happen. this means that the argument parsing logic has a bug.")
            exit(1)

        if run_type == "cli":
            self._run_cli()
            return

        if run_type == "cmd":
            self._run_cmd()
            return

        if run_type != "file":
            print(f"run type: {run_type} is not supported. this error should never happen. this means that the argument parsing logic has a bug.")
            exit(1)

        # open and load the file
        vprint(f"Opening file: {file_path}...")
        Interpreter.code = self._load_code_from_file(file_path)

            
        vvprint(indent(Interpreter.code))

        # Preprocess the code
        vprint("Preprocessing code...")
        Interpreter.code = PreProcessor().run(Interpreter.code)
        vvprint(indent(Interpreter.code))

        vprint("parsing code...")
        # TODO: parse the code here
        vvprint(indent("parsed code goes here"))

        vprint("Building AST...")
        # TODO: Build the AST here
        vvprint(indent("AST goes here"))

        vprint("Executing code...")
        # TODO: Execute the code here
        vvprint(indent("execution result goes here"))


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

    def _run_cmd(self):
        for code in ArgumentHandler().args:
            pass
            # TODO: Implement the actual code execution logic

    def _load_code_from_file(self, file_path):
        with open(file_path, "r") as f:
            code = f.read()
            return code
