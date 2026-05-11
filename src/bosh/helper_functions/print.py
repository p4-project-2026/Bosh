import json

from bosh.app.cli.flags.flags import Verbose
from bosh.app.cli.flags.flags import VeryVerbose
from bosh.app.cli.flags.flags import VeryVeryVerbose

_verbose_flag_proceeded = False
_print_queue = []

def vprint(*args, **kwargs):
    global _verbose_flag_proceeded

    _flush_print_queue()

    if not _verbose_flag_proceeded:
        _print_queue.append((*args, "v"))
        return
        
    if Verbose.enabled or VeryVerbose.enabled or VeryVeryVerbose.enabled:
        print(*args, **kwargs)

def vvprint(*args, **kwargs):
    global _verbose_flag_proceeded

    _flush_print_queue()

    if not _verbose_flag_proceeded:
        _print_queue.append((*args, "vv"))
        return

    if VeryVerbose.enabled or VeryVeryVerbose.enabled:
        print(*args, **kwargs)

def vvvprint(*args, **kwargs):
    global _verbose_flag_proceeded

    _flush_print_queue()

    if not _verbose_flag_proceeded:
        _print_queue.append((*args, "vvv"))
        return

    if VeryVeryVerbose.enabled:
        print(*args, **kwargs)

def indent(*args, indent_level=4):
    indent_str = ' ' * indent_level
    result = []
    for arg in args:
        result.append(indent_str + str(arg).replace("\n", "\n" + indent_str))
    return "\n".join(result)

def json_format(json_data):
    return str(json.dumps(json_data, indent=4))

def _flush_print_queue():
    global _verbose_flag_proceeded
    global _print_queue

    if not _print_queue: return
    if not _verbose_flag_proceeded: return

    for (*arg, type) in _print_queue:
        match type:
            case "v":
                if Verbose.enabled or VeryVerbose.enabled or VeryVeryVerbose.enabled: print(*arg)
            case "vv":
                if VeryVerbose.enabled or VeryVeryVerbose.enabled: print(*arg)
            case "vvv":
                if VeryVeryVerbose.enabled: print(*arg)
    _print_queue = []

def set_verbose_flag_proceeded(arg):
    global _verbose_flag_proceeded
    _verbose_flag_proceeded = arg