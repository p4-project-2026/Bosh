import inspect
from . import flags as flags_module

class FlagHandler:
    # Dynamically gather all flag classes defined in flags.py
    # Preserve the definition order from flags_module by iterating over its __dict__
    flags = [
        obj for name, obj in flags_module.__dict__.items()
        if inspect.isclass(obj) and obj.__module__ == flags_module.__name__ and not name.startswith("_") 
    ]

    def set_flags_by_args(self, args):
        for arg in args:          
            # Check if the argument matches any flag
            for Flag in self.flags:
                if Flag.aliases and arg in Flag.aliases:
                    Flag.enabled = True
            # unrecognized flag, you can choose to print a warning or ignore
            else:
                print(f"Error: Unrecognized flag '{arg}'")
                self.flags[0].runner()  # Show help and exit

    def execute_before_flags(self):
        for flag in self.get_enabled_flags():
            if flag.run_type == "before":
                flag.runner()

    def execute_after_flags(self):
        for flag in self.get_enabled_flags():
            if flag.run_type == "after":
                flag.runner()

    def get_enabled_flags(self):
        return [flag for flag in self.flags if flag.enabled]