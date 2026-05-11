# app imports
from bosh.app.cli.arguments.argument_handler import ArgumentHandler
from bosh.app.cli.cli_handler import CLIHandler
from bosh.app.config.config_handler import ConfigHandler

# interpreter imports
from bosh.interpreter.interpreter import Interpreter

# helper function imports
from bosh.helper_functions.print import vprint, vvprint, vvvprint

class Main:
    def run(self):
        vprint("Starting Bosh...")

        # Initialize configuration and setup
        ConfigHandler().initializer()

        # Cli initializer
        CLIHandler().initializer()

        # run Interpreter
        Interpreter().run(ArgumentHandler.file, CLIHandler.run_type)

        # Cli terminator
        CLIHandler().terminator()

        vprint("Bosh finished execution!")





# Entry point for command line execution
if __name__ == "__main__":
    Main().run()

# Alternative entry point for uv
def main():
    Main().run()