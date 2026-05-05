import importlib.metadata
import msvcrt
import sys

class Help:
	name = "help"
	aliases = ("-h", "--help")
	description = "Show help information."
	enabled = False
	run_type = "before"

	@staticmethod
	def runner():
		_current_module = sys.modules[__name__]
		_flag_objects = []
		
        # Dynamically gather all flag classes defined in this module in declaration order
		for name in dir(_current_module):
			obj = getattr(_current_module, name)
			if isinstance(obj, type) and hasattr(obj, 'aliases') and hasattr(obj, 'description'):
				_flag_objects.append((obj, getattr(obj, '__module__', ''), getattr(obj, '__qualname__', name)))
		
		# Sort by class definition order using source line number
		try:
			import inspect
			_flag_objects.sort(key=lambda x: inspect.getsourcelines(x[0])[1])
		except:
			pass
		_flag_objects = [obj[0] for obj in _flag_objects]
				
        # Calculate maximum length of aliases for formatting
		max_alias_len = max(len(', '.join(obj.aliases)) for obj in _flag_objects) if _flag_objects else 0

        # Print usage and flag information
		print("Usage: bosh [flags] [file] [args]\n")
		print(f"{'Flags:':<{max_alias_len+5}} Descriptions:")
		
        # Print each flag with its aliases and description
		for obj in _flag_objects:
			name_aliases = f"{', '.join(obj.aliases)}"
			print(f"  {name_aliases:<{max_alias_len+5}} {obj.description}")
		exit(0)

class Version:
    name = "version"
    aliases = ("-V", "--version")
    description = "Show version information."
    enabled = False
    run_type = "before"

    @staticmethod
    def runner():
        version = importlib.metadata.version("bosh")
        print(f"Bosh version: {version}")
        exit(0)

class Verbose:
	name = "verbose"
	aliases = ("-v", "--verbose")
	description = "Enable verbose output."
	enabled = False
	run_type = "value"
	
class VeryVerbose:
	name = "very-verbose"
	aliases = ("-vv", "--vverbose")
	description = "Enable very verbose output."
	enabled = False
	run_type = "value"

class VeryVeryVerbose:
    name = "very-very-verbose"
    aliases = ("-vvv", "--vvverbose")
    description = "Enable very very verbose output."
    enabled = False
    run_type = "value"

class Pause:
	name = "pause"
	aliases = ("-p", "--pause")
	description = "pause execution before exiting."
	enabled = False
	run_type = "after"

	@staticmethod
	def runner():
		print("Press any key to continue...")
		msvcrt.getch()

	



    