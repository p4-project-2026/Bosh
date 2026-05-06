# tomlib is only read
from bosh.helper_functions.paths import PathsHelper
import tomllib

class ConfigHandler:
    config = {}

    def initilize(self):
        # Check if config file exists, if not create it
        config_path = self._get_config_file_path()
        if not config_path.exists():
            self._create_default_config()

        # Load the config file
        self._load_config(config_path)

    def _get_config_file_path(self):
        # Get the config file path based on how the project is run
        return PathsHelper().get_project_root().joinpath("config.toml")

    def _create_default_config(self):
        # Create a default config file
        default_config = self._get_default_config()
        config_path = self._get_config_file_path()
        with open(config_path, "wb") as f:
            f.write(default_config)

    def _get_default_config(self):
        default_config_path = PathsHelper().get_src_path().joinpath("bosh/app/config/default_config.toml")
        with open(default_config_path, "rb") as f:
            return f.read()
        
    def _load_config(self, config_path):
        with open(config_path, "rb") as f:
            self.config = tomllib.load(f)