class ArgumentHandler:
    args = []

    def extract_args(self, args):
        for arg in args:
            if not arg.startswith('-'): self.args.append(arg)

    def get_args(self):
        return self.args