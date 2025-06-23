import tkinter as tk
from tkinter import filedialog, messagebox
import keyword
import os
import matplotlib.pyplot as plt
from check_for_updates import check_for_updates

class SimpleIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Python IDE")

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

        self.update_line_numbers()

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
    # Run update check before actual app
    check_for_updates()
    
    root = tk.Tk()
    ide = SimpleIDE(root)
    root.mainloop()

