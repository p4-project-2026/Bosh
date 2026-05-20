import sys
import subprocess
from bosh.helper_functions.paths import PathsHelper

def build():
    source = PathsHelper().get_project_root().joinpath("src/bosh/app/bosh.py")
    
    if not source.exists():
        print(f"Error: Source file not found at {source}")
        sys.exit(1)
    
    print(f"Building {source}...")
    
    subprocess.run([
        "pyinstaller", 
        "--noconfirm", 
        "--onedir", 
        "--console",
        "--add-data", "src/bosh/app/config/default_config.toml;bosh/app/config",
        "--add-data", "src/bosh/interpreter/lexparser/bosh_lang.lark;bosh/interpreter/lexparser",
        str(source)
    ], check=True)

    print("Build completed successfully!")

if __name__ == "__main__":
    build()
