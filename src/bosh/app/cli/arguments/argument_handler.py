import sys
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

        # if no arguments or file, return
        if len(args) == 0:
            vprint("no file provided")
            vprint("no aruments provided")
            return

        if args[0].endswith(".bosh"):
            # file and arguments
            ArgumentHandler.file = args[0]
            ArgumentHandler.args = args[1:]
            vprint(f"file: {ArgumentHandler.file}")
            vprint(f"arguments: {ArgumentHandler.args}")
        elif len(args) != 0:
            # no file, just arguments
            ArgumentHandler.args = args
            vprint("no file provided")
            vprint(f"arguments: {ArgumentHandler.args}")

    def get_run_type(self):
        # get values
        cmd_flag = Cmd.enabled
        file = ArgumentHandler.file
        args = ArgumentHandler.args

        # bit logics
        # flags:
        if cmd_flag == False: cmd_flag = "0"
        else: cmd_flag = "1"
        # file:
        if file is None: file = "0"
        else: file = "1"
        # args:
        if len(args) == 0: args = "0"
        else: args = "1"

        # combine into a binary string
        bits = args + file + cmd_flag

        # switch case for run type
        match bits:
            case "000": return "cli"
            case "001": return "cli"
            case "010": return "file"
            case "011": raise RunTypeError(message="Cannot run cmd flag and file at the same time!")
            case "100": return "cli"
            case "101": return "cmd"
            case "110": return "file"
            case "111": raise RunTypeError(message="Cannot run cmd flag and file at the same time!")