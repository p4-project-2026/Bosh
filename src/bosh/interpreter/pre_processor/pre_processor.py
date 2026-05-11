class PreProcessor:
    def __init__(self, code):
        self.code = code

    def run(self):
        self._whitespace_strip()
        self.insert_symbols_at_nested_indents()

    
    def _whitespace_strip(self):
        self.code = self.code.strip()
        return self.code

    def insert_symbols_at_nested_indents(self):
        # Insert {} around nested blocks of indented code.
        lines = self.code.splitlines()
        indent_stack = [0]
        
        for i, line in enumerate(lines):
            if not line.strip():  # Skip empty lines
                continue
            
            current_indent = len(line) - len(line.lstrip())
            
            # If the current indentation is the same as the last one, just continue
            if current_indent == indent_stack[-1]:
                continue
            
            if i == 0:  # Don't modify before first line
                continue
            
            # If the current indentation is greater than the last one, we are entering a new block
            if current_indent > indent_stack[-1]:
                lines[i - 1] += " {"
                indent_stack.append(current_indent)
            else: # We are exiting one or more blocks
                # If the current indentation doesn't match any previous indentation level, it's an error
                if not current_indent in indent_stack:
                    print(f"Error: Inconsistent indentation at line {i + 1}\nTODO: add proper error handling for this")
                    exit(1)

                # if there are multiple levels of indentation to close, we need to add closing braces for each level
                while current_indent < indent_stack[-1]:
                    lines[i - 1] += "}"
                    indent_stack.pop()
        
        # Close remaining open blocks at the end of the code
        while len(indent_stack) > 1:
            lines[-1] += "}"
            indent_stack.pop()
        
        # Join the lines back into a single string
        self.code = "\n".join(lines)
        return self.code