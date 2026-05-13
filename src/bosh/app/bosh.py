# app imports
from bosh.app.global_imports.global_importer import GlobalImporter
from bosh.app.cli.arguments.argument_handler import ArgumentHandler
from bosh.app.cli.cli_handler import CLIHandler
from bosh.app.config.config_handler import ConfigHandler

# interpreter imports
from bosh.interpreter.interpreter import Interpreter

# helper function imports
from bosh.helper_functions.print import print_error

class Main:
    def run(self):
        # Setup global imports
        GlobalImporter().import_all()

        vprint("Starting Bosh...")

        # Initialize configuration and setup
        ConfigHandler().initializer()

        # Cli initializer
        try:
            CLIHandler().initializer()
        except Exception as e:
            raise CLIError(f"Error initializing CLI", cause=e)

        # run Interpreter
        try:
            Interpreter().run(ArgumentHandler.file, CLIHandler.run_type)
        except Exception as e:
            raise BoshRuntimeError(f"Error running interpreter: {e}", cause=e)

        # Cli terminator
        CLIHandler().terminator()

        vprint("Bosh finished execution!")





# Entry point for command line execution
if __name__ == "__main__":
    try:
        Main().run()
    except Exception as e:
        print_error(f"Error when running Bosh:", e)

# Alternative entry point for uv
def main():
    try:
        Main().run()
    except Exception as e:
        print_error(f"Error when running Bosh:", e)