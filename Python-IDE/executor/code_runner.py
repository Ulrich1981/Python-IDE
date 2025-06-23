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
            exec_globals = {'__name__': '__main__'}
            exec(code, exec_globals)
            self.console.write(buffer.getvalue())

            # Check for active figure
            if plt.get_fignums():
                self.console.display_plot()
                plt.close('all')

        except Exception:
            self.console.write(traceback.format_exc())
        finally:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
