from bosh.app.cli.cli_handler import CLIHandler
from bosh.app.config.config_handler import ConfigHandler
from bosh.helper_functions.print import vprint, vvprint, vvvprint

class Main:
    def run(self):
        # Initialize configuration and setup
        ConfigHandler().initializer()

        # Cli initializer
        CLIHandler().initializer()

        # run Interpreter


        # Cli terminator
        CLIHandler().terminator()





# Entry point for command line execution
if __name__ == "__main__":
    Main().run()

# Alternative entry point for uv
def main():
    Main().run()