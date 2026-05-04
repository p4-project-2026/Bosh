import sys
from pathlib import Path
import subprocess

def build():
    source = Path(__file__).parent.parent / "bosh" / "bosh.py"
    
    if not source.exists():
        print(f"Error: Source file not found at {source}")
        sys.exit(1)
    
    print(f"Building {source}...")
    
    subprocess.run(["pyinstaller", "--noconfirm", "--onedir", "--console", str(source)], check=True)

    print("Build completed successfully!")

if __name__ == "__main__":
    build()
