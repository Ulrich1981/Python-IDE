# Run update check before actual app
from check_for_updates import check_for_updates
check_for_updates()

import tkinter as tk
from tkinter import filedialog, messagebox
import keyword
import os
import sys
import threading
import traceback
import subprocess
import importlib
import ast
import io


def get_missing_imports(code):
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


class PythonIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Python IDE with Auto Package Install & Chart Support")

        self.filename = None
        self.breakpoints = set()

        # Menu
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.load_file)
        filemenu.add_command(label="Save", command=self.save_file)
        filemenu.add_command(label="Save As", command=self.save_as_file)
        menubar.add_cascade(label="File", menu=filemenu)
        root.config(menu=menubar)

        # Text Editor + Scrollbar
        self.text = tk.Text(root, undo=True, wrap='none', font=('Courier', 12))
        self.text.pack(fill=tk.BOTH, expand=1)
        self.text.bind("<KeyRelease>", self.syntax_highlight)

        # Line numbers and breakpoints
        self.line_numbers = tk.Canvas(root, width=40, bg="#f0f0f0")
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.text.bind("<KeyRelease>", lambda e: self.update_line_numbers())
        self.line_numbers.bind("<Button-1>", self.toggle_breakpoint)

        self.console = tk.Text(root, height=10, bg='black', fg='white')
        self.console.pack(fill=tk.X)

        self.update_line_numbers()

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
        missing = get_missing_imports(code)
        if missing:
            msg = "Missing packages detected:\n" + "\n".join(missing) + "\nInstall now?"
            if messagebox.askyesno("Missing Packages", msg):
                for pkg in missing:
                    self.write_console(f"Installing {pkg}...")
                    subprocess.call([sys.executable, "-m", "pip", "install", pkg])
        self._safe_exec(code)

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

    def save_file(self):
        if self.filename:
            with open(self.filename, 'w') as f:
                f.write(self.text.get("1.0", tk.END))
        else:
            self.save_as_file()

    def save_as_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".py")
        if path:
            self.filename = path
            self.save_file()
            self.root.title(f"Python IDE - {os.path.basename(path)}")

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if path:
            with open(path, 'r') as f:
                self.text.delete("1.0", tk.END)
                self.text.insert("1.0", f.read())
            self.filename = path
            self.root.title(f"Python IDE - {os.path.basename(path)}")
            self.update_line_numbers()
            self.syntax_highlight(None)

    def update_line_numbers(self):
        self.line_numbers.delete("all")
        i = self.text.index("@0,0")
        while True:
            dline = self.text.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            color = "red" if int(linenum) in self.breakpoints else "black"
            self.line_numbers.create_text(2, y, anchor="nw", text=linenum, fill=color)
            i = self.text.index(f"{i}+1line")

    def toggle_breakpoint(self, event):
        index = self.text.index(f"@0,{event.y}")
        linenum = int(index.split(".")[0])
        if linenum in self.breakpoints:
            self.breakpoints.remove(linenum)
        else:
            self.breakpoints.add(linenum)
        self.update_line_numbers()

    def syntax_highlight(self, event):
        self.text.tag_remove("keyword", "1.0", tk.END)
        content = self.text.get("1.0", tk.END)
        for word in keyword.kwlist:
            idx = "1.0"
            while True:
                idx = self.text.search(rf"\b{word}\b", idx, nocase=0, stopindex=tk.END, regexp=True)
                if not idx:
                    break
                end = f"{idx}+{len(word)}c"
                self.text.tag_add("keyword", idx, end)
                idx = end
        self.text.tag_config("keyword", foreground="blue")


if __name__ == "__main__":
    root = tk.Tk()
    ide = PythonIDE(root)
    root.mainloop()
