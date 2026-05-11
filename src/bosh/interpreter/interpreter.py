from bosh.helper_functions.print import vprint
class Interpreter:
    def run(self, file_path, run_type):
        vprint(f"Running {file_path} with run type: {run_type}")
        