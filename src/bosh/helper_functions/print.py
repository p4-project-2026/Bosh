import json

from bosh.app.cli.flags.flags import Verbose
from bosh.app.cli.flags.flags import VeryVerbose
from bosh.app.cli.flags.flags import VeryVeryVerbose

def vprint(*args, **kwargs):
    if Verbose.enabled or VeryVerbose.enabled or VeryVeryVerbose.enabled:
        print(*args, **kwargs)

def vvprint(*args, **kwargs):
    if VeryVerbose.enabled or VeryVeryVerbose.enabled:
        print(*args, **kwargs)

def vvvprint(*args, **kwargs):
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

queue = []
def print_queue(*arg, type):
    queue.append((*arg, type))
def flush_print_queue():
    for (*arg, type) in queue:
        match type:
            case "v":
                vprint(*arg)
            case "vv":
                vvprint(*arg)
            case "vvv":
                vvvprint(*arg)