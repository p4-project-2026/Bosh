# Bosh Language Support

Syntax highlighting and editor support for `.bosh` files.

## Features

- Syntax highlighting
- Comments with `#`
- Bracket matching
- String interpolation highlighting

## Installation

### Option 1: Install manually without Node.js

This is the easiest local installation method.

1. Close VS Code.

2. Copy this folder:

        Bosh/editor/vscode

3. Paste it into your VS Code extensions folder and rename it:

        C:\Users\<your-user-name>\.vscode\extensions\bosh-language-support

   Example:

        C:\Users\micha\.vscode\extensions\bosh-language-support

4. Reopen VS Code.

5. Open a `.bosh` file.

6. The language mode in the bottom-right corner should show `Bosh`.

If it still says `Plain Text`, click `Plain Text` and select `Bosh`.

---

### Option 2: Install from a `.vsix` package

This requires Node.js and npm.

1. Install the Node.js LTS version.

2. Close and reopen VS Code or PowerShell.

3. Check that Node.js and npm are available:

        node --version
        npm --version

4. Install the VS Code extension packaging tool:

        npm install -g @vscode/vsce

5. Go to the extension folder:

        cd "C:\Users\micha\Documents\VS code\Bosh\editor\vscode"

6. Build the `.vsix` package:

        vsce package

7. Install the generated `.vsix` file:

        code --install-extension .\bosh-language-support-0.0.1.vsix

8. Restart VS Code and open a `.bosh` file.

---

## Development

To test the extension while editing it:

1. Open this folder in VS Code:

        Bosh/editor/vscode

2. Press `F5`.

This opens a new VS Code window called the **Extension Development Host**. In that window, open a `.bosh` file to test the syntax highlighting.