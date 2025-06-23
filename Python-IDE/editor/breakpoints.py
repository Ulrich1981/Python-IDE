class BreakpointManager:
    def __init__(self):
        self.breakpoints = set()

    def toggle(self, line_number):
        if line_number in self.breakpoints:
            self.breakpoints.remove(line_number)
        else:
            self.breakpoints.add(line_number)

    def is_breakpoint(self, line_number):
        return line_number in self.breakpoints
