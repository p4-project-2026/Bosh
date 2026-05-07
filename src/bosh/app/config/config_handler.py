# tomlib is only read
from bosh.app.cli.flags.flag_handler import FlagHandler
from bosh.helper_functions.paths import PathsHelper
import tomllib

from pprint import pprint
from bosh.helper_functions.print import print_queue, json_format, indent

class ConfigHandler:
    config = None
    default_config = None

    def initializer(self):
        # Check if config file exists, if not create it
        config_path = self._get_config_file_path()
        if not config_path.exists():
            print_queue("Config file not found, creating default config file...", type="v")
            self._create_default_config()

        # Load the config file
        self._load_config(config_path)
        print_queue("config loaded!", type="v")
        print_queue(indent(json_format(self.config)), type="vv")

        # set default flags
        self.set_default_flags(self.get("bosh.default_flags"))      
        
    def get(self, path=None):
        if path is None: return self.config

        # Get a value from the config file using a dot separated path
        keys = path.split(".")
        value = self.config
        for key in keys:
            value = value[key]
        return value

    def _get_config_file_path(self):
        # Get the config file path based on how the project is run
        return PathsHelper().get_project_root().joinpath("config.toml")

    def _create_default_config(self):
        # Create a default config file
        default_config = self._get_default_config()
        config_path = self._get_config_file_path()
        with open(config_path, "wb") as f:
            f.write(default_config)

    def _load_default_config(self):
        if self.default_config is not None:
            return self.default_config
        
        default_config_path = PathsHelper().get_src_path().joinpath("bosh/app/config/default_config.toml")
        with open(default_config_path, "rb") as f:
            self.default_config = f.read()
            return self.default_config

    def _load_config(self, config_path):
        with open(config_path, "rb") as f:
            self.config = tomllib.load(f)

    def _get_default_config(self):
        return self._load_default_config()
    
    def set_default_flags(self, flags):
        FlagHandler().set_flags_by_args(flags)