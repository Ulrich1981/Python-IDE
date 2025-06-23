import tkinter as tk
from tkinter import messagebox
import sys
import threading
import traceback
import subprocess
import importlib
import ast
import io
import contextlib
import matplotlib.pyplot as plt
import check_for_updates

class PythonIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Python IDE with Auto Package Install & Chart Support")

        self.text = tk.Text(root, undo=True, wrap='none', font=('Courier', 12))
        self.text.pack(fill=tk.BOTH, expand=1)

        self.console = tk.Text(root, height=10, bg='black', fg='white')
        self.console.pack(fill=tk.X)

        self.highlight_tag = "current_line"
        self.text.tag_configure(self.highlight_tag, background="yellow")

        button_frame = tk.Frame(root)
        button_frame.pack(fill=tk.X)
        tk.Button(button_frame, text="Run", command=self.run_code).pack(side=tk.LEFT)
        tk.Button(button_frame, text="Step", command=self.step_run).pack(side=tk.LEFT)

        self.code_lines = []
        self.current_line_index = 0

    def run_code(self):
        self.console.delete(1.0, tk.END)
        code = self.text.get("1.0", tk.END)
        threading.Thread(target=self._run_with_dependencies, args=(code,)).start()

    def _run_with_dependencies(self, code):
        missing = self.get_missing_imports(code)
        if missing:
            msg = "Missing packages detected:\n" + "\n".join(missing) + "\nInstall now?"
            if messagebox.askyesno("Missing Packages", msg):
                for pkg in missing:
                    self.write_console(f"Installing {pkg}...")
                    subprocess.call([sys.executable, "-m", "pip", "install", pkg])
        self._safe_exec(code)

    def get_missing_imports(self, code):
        required = set()
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    required.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    required.add(node.module.split('.')[0])
        missing = []
        for mod in required:
            try:
                importlib.import_module(mod)
            except ImportError:
                missing.append(mod)
        return missing

    def _safe_exec(self, code):
        try:
            stdout = sys.stdout
            stderr = sys.stderr
            sys.stdout = sys.stderr = io.StringIO()
            exec_globals = {}
            exec(code, exec_globals)
            output = sys.stdout.getvalue()
            self.write_console(output)
        except Exception:
            self.write_console(traceback.format_exc())
        finally:
            sys.stdout = stdout
            sys.stderr = stderr

    def step_run(self):
        if not self.code_lines:
            code = self.text.get("1.0", tk.END).splitlines()
            self.code_lines = code
            self.current_line_index = 0
            self.console.delete(1.0, tk.END)

        if self.current_line_index >= len(self.code_lines):
            self.code_lines = []
            self.write_console("Execution finished.")
            return

        line = self.code_lines[self.current_line_index]
        self.highlight_line(self.current_line_index + 1)
        self.write_console(f">>> {line.strip()}")

        try:
            exec(line, globals())
        except Exception:
            self.write_console(traceback.format_exc())

        self.current_line_index += 1

    def highlight_line(self, lineno):
        self.text.tag_remove(self.highlight_tag, "1.0", tk.END)
        self.text.tag_add(self.highlight_tag, f"{lineno}.0", f"{lineno}.0 lineend")
        self.text.see(f"{lineno}.0")

    def write_console(self, text):
        self.console.insert(tk.END, text.strip() + "\n")
        self.console.see(tk.END)

if __name__ == "__main__":
    # Run update check before actual app
    check_for_updates()
    
    root = tk.Tk()
    ide = PythonIDE(root)
    root.mainloop()

