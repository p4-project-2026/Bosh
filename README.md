# Bosh  
*Beginner‑Oriented Shell*

## Description  
*Bosh* (Beginner‑Oriented SHell) is a scripting language built with an emphasis on readability and accessibility for casual programmers.  
Bosh introduces an English‑Like Language syntax that allows users to express file automation using natural English sentences and intuitive verbs.

## Installation

### Windows  
1. Download the latest Windows ZIP from the GitHub Releases page.  
2. Unzip it to any folder you like (e.g., `C:\Tools\Bosh`).  
3. Add that folder to your system’s PATH environment variable.  
4. Open a new terminal so PATH updates.  

You can now run Bosh from anywhere using the `bosh` command.

### Linux (Unofficial Support via UV)  
There is no official Linux build, but Linux users can run Bosh using UV.

1. Install UV (if you don’t already have it):  
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Clone the Bosh repository:  
   ```bash
   git clone https://github.com/p4-project-2026/Bosh.git
   cd bosh
   ```

3. Sync the UV environment:  
   ```bash
   uv sync
   ```

4. Run Bosh using UV:  
   ```bash
   uv run bosh <your-script.bosh>
   ```

## Usage

### Command Structure

```bash
bosh [-flags] [file] [args]
```

- **Default script behavior** — If no valid file is provided, Bosh runs the default script: `script.bosh` *(Configurable)*  
- **Flag behavior** — Flags modify how Bosh runs and can be preset in the config *(Configurable)*  
- **Argument passing** — Any additional arguments are injected into the script as `Arg1`, `Arg2`, `Arg3`, etc.

### Examples
Run a script:
```bash
bosh myscript.bosh
```

## Flags

| Flag | Aliases | Description |
|------|---------|-------------|
| Help | `-h`, `--help` | Show help information and exit. |
| Version | `-V`, `--version` | Show Bosh version information and exit. |
| Verbose | `-v`, `--verbose` | Enable verbose output. |
| Very Verbose | `-vv`, `--vverbose` | Enable very verbose output. |
| Very Very Verbose | `-vvv`, `--vvverbose` | Enable very very verbose output. |
| Trace | `-t`, `--trace` | Show full execution trace through ifs and loops. |
| Pause | `-p`, `--pause` | Pause execution before exiting (waits for keypress). |
| Cmd | `-c`, `--cmd` | Run the arguments directly instead of a file. |

## Example Bosh Script
Some coding examples can be found in the coding examples directory.

## Configuration
Bosh supports optional configuration for customizing behavior.  
A default configuration file typically looks like this:

```toml
[bosh]
default_file = "script.bosh"
default_flags = []
```

## Testing
Bosh includes a small test suite to verify core functionality and ensure the interpreter behaves consistently across updates.

### Running All Tests
```bash
pytest
```

### Filtering Tests
```bash
pytest -k "interpreter"
```

## Build  
For advanced users who want to build Bosh from source:
```bash
uv run build
```
