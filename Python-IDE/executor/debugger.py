class Debugger:
    def __init__(self):
        self.breakpoints = set()

    def set_breakpoints(self, lines):
        self.breakpoints = set(lines)

    def should_pause(self, lineno):
        return lineno in self.breakpoints
