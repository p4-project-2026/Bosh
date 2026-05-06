import msvcrt

from bosh.app.config.config_handler import ConfigHandler
from bosh.app.setup.flags.flag_handler import FlagHandler
from bosh.app.setup.arguments.argument_handler import ArgumentHandler

class Main:
    def run(self):
        # Initialize configuration and setup
        ConfigHandler().initilize()

        # Set flags based on command line arguments
        FlagHandler().set_flags_by_args(self.get_args())
        
        # Execute any "before" flags
        FlagHandler().execute_before_flags()

        # extract the non-flag arguments for your main application logic
        ArgumentHandler().extract_args(self.get_args())
        

        # run the main logic of your application here


        # Execute any "after" flags
        FlagHandler().execute_after_flags()

        print("Press any key to exit...")
        msvcrt.getch()


    def get_args(self):
        import sys
        return sys.argv[1:]



# Entry point for command line execution
if __name__ == "__main__":
    Main().run()

# Alternative entry point for uv
def main():
    Main().run()