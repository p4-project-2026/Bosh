# Bosh Language Support for VS Code

This extension adds syntax highlighting and basic editor support for `.bosh` files in Visual Studio Code.

## Features

- Syntax highlighting for Bosh code
- Highlighting for comments, strings, numbers, dates, booleans, functions, tasks, control flow, list operations, text operations, file operations, and operators
- Bracket matching for `{}`, `()`, and `[]`
- Auto-closing brackets and strings
- Line comments using `#`

## Installation

The extension is installed from a `.vsix` file.

A `.vsix` file is a local VS Code extension installer.

### Install using VS Code

1. Open Visual Studio Code.

2. Open the Extensions view:

        Ctrl + Shift + X

3. Click the `...` menu in the top-right corner of the Extensions panel.

4. Choose:

        Install from VSIX...

5. Select the Bosh `.vsix` file, for example:

        bosh-language-support-0.0.1.vsix

6. Restart VS Code if prompted.

7. Open a `.bosh` file.

8. The language mode in the bottom-right corner should show:

        Bosh

If it says `Plain Text`, click `Plain Text`, then select `Bosh`.

## Install using the command line

You can also install the extension from a terminal.

Open PowerShell or a terminal in the folder containing the `.vsix` file and run:

        code --install-extension bosh-language-support-0.0.1.vsix

Then restart VS Code and open a `.bosh` file.

## Updating the Extension

To update the extension, install the newer `.vsix` file the same way.

For example:

        code --install-extension bosh-language-support-0.0.2.vsix

VS Code will replace the older version with the newer one.

## Uninstalling

1. Open the Extensions view:

        Ctrl + Shift + X

2. Search for:

        Bosh Language Support

3. Click the gear icon.

4. Choose:

        Uninstall

5. Restart VS Code if prompted.

## Development

This section is only for people editing the extension itself.

Open this folder in VS Code:

        Bosh/editor/vscode

Press:

        F5

This opens a new VS Code window called the Extension Development Host.

In that new window, open a `.bosh` file to test the syntax highlighting.

After editing `syntaxes/bosh.tmLanguage.json`, reload the Extension Development Host window:

        Ctrl + Shift + P

Then run:

        Developer: Reload Window

## Building the VSIX

This section is only for maintainers.

Install Node.js LTS first. This provides `node` and `npm`.

Check that they are installed:

        node --version
        npm --version

Install the VS Code extension packaging tool:

        npm install -g @vscode/vsce

From this folder:

        Bosh/editor/vscode

build the `.vsix` file:

        vsce package

This creates a file like:

        bosh-language-support-0.0.1.vsix

That file can be shared with users so they can install the Bosh extension in VS Code.