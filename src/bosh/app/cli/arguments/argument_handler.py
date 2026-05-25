import sys
from bosh.app.config.config_handler import ConfigHandler
from bosh.helper_functions.print import vprint
from bosh.app.cli.flags.flags import Cmd

class ArgumentHandler:
    flags = []
    file = None
    args = []

    def extract_args_from_cli(self):
        args = sys.argv[1:]

        # flags
        for arg in args:
            if arg.startswith('-'):
                ArgumentHandler.flags.append(arg)
            else: break

        vprint(f"flags: {ArgumentHandler.flags}")

        # non-flag arguments
        args = args[len(ArgumentHandler.flags):]

        if len(args) == 0:
            ArgumentHandler.file = ConfigHandler().get(path = "bosh.default_file")
            vprint("no file provided, default file used")
            vprint(f"arguments: {ArgumentHandler.args}")
            return

        if args[0].endswith(".bosh"):
            # file and arguments
            ArgumentHandler.file = args[0]
            ArgumentHandler.args = args[1:]
            vprint(f"file: {ArgumentHandler.file}")
            vprint(f"arguments: {ArgumentHandler.args}")
        else:
            # no file, just arguments
            ArgumentHandler.args = args
            ArgumentHandler.file = ConfigHandler().get(path = "bosh.default_file")
            vprint("no file provided, default file used")
            vprint(f"arguments: {ArgumentHandler.args}")