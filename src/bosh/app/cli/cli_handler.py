from bosh.app.cli.arguments.argument_handler import ArgumentHandler
from bosh.app.cli.flags.flag_handler import FlagHandler
from bosh.helper_functions.print import flush_print_queue

class CLIHandler:
    run_type = None

    def initializer(self):
        # extract the non-flag arguments for your main application logic
        ArgumentHandler().extract_args_from_cli()

        # set flags based on command line arguments
        FlagHandler().set_flags_by_args(ArgumentHandler.flags)

        # flush the print queue
        flush_print_queue()

        # get_run_type
        CLIHandler.run_type = ArgumentHandler().get_run_type()

        # execute before flags
        FlagHandler().execute_before_flags()

    def terminator(self):
        # execute after flags
        FlagHandler().execute_after_flags()