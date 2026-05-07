import sys
from bosh.helper_functions.print import print_queue
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

        print_queue("flags: " + str(ArgumentHandler.flags), type="v")

        # non-flag arguments
        args = args[len(ArgumentHandler.flags):]

        # if no arguments or file, return
        if len(args) == 0:
            print_queue("no file provided", type="v")
            print_queue("no aruments provided", type="v")
            return

        if args[0].endswith(".bosh"):
            # file and arguments
            ArgumentHandler.file = args[0]
            ArgumentHandler.args = args[1:]
            print_queue(f"file: {ArgumentHandler.file}", type="v")
            print_queue(f"arguments: {ArgumentHandler.args}", type="v")
        elif len(args) != 0:
            # no file, just arguments
            ArgumentHandler.args = args
            print_queue("no file provided", type="v")
            print_queue("arguments: " + str(ArgumentHandler.args), type="v")

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
            case "011": return "err"
            case "100": return "cli"
            case "101": return "cmd"
            case "110": return "file"
            case "111": return "err"
            case _: return "err"