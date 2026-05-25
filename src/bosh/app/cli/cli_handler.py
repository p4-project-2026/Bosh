from bosh.app.cli.arguments.argument_handler import ArgumentHandler
from bosh.app.cli.flags.flag_handler import FlagHandler

from bosh.app.cli.flags.flags import Cmd
class CLIHandler:
    def initializer(self):
        # extract the non-flag arguments for your main application logic
        ArgumentHandler().extract_args_from_cli()

        # set flags based on command line arguments
        FlagHandler().set_flags_by_args(ArgumentHandler.flags)

        # Mark that verbose flags have been processed and queued messages should be flushed
        from bosh.helper_functions.print import set_verbose_flag_proceeded
        set_verbose_flag_proceeded(True)

        # execute before flags
        FlagHandler().execute_before_flags()

    def terminator(self):
        # execute after flags
        FlagHandler().execute_after_flags()