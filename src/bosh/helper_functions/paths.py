import sys
from pathlib import Path


class PathsHelper:
    project_root = None

    def get_project_root(self):
        """Get the root directory based on how the project is run.
        When frozen (as exe): returns the directory where the exe is located
        When running from source: returns the project root (where pyproject.toml is)
        """
        if self.project_root is not None:
            return self.project_root

        # When running as a frozen PyInstaller executable, use exe directory
        if getattr(sys, "frozen", False):
            self.project_root = Path(sys.executable).parent
            return self.project_root

        current_path = Path(__file__).resolve()

        for parent in current_path.parents:
            if (parent / "pyproject.toml").exists():
                self.project_root = parent
                return parent

        self.project_root = current_path.parent
        return current_path.parent
    
    def get_src_path(self):
        if getattr(sys, "frozen", False):
            return self.get_project_root().joinpath("_internal")
        return self.get_project_root().joinpath("src")
