import traceback
import io
import sys

class CodeRunner:
    def __init__(self, editor, console):
        self.editor = editor
        self.console = console

    def run_code(self):
        code = self.editor.text.get("1.0", "end-1c")
        self.console.clear()
        buffer = io.StringIO()
        try:
            sys.stdout = sys.stderr = buffer
            exec(code, {})
        except Exception:
            traceback.print_exc()
        finally:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            self.console.write(buffer.getvalue())
