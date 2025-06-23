import tkinter as tk
from editor.syntax_highlighter import SyntaxHighlighter

class TextEditor(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.text = tk.Text(self, undo=True, wrap='none', font=('Courier', 12))
        self.text.pack(fill=tk.BOTH, expand=1)
        self.syntax = SyntaxHighlighter(self.text)
        self.text.bind("<KeyRelease>", self.syntax.highlight)
