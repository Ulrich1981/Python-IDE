import tkinter as tk

class ConsoleOutput(tk.Text):
    def __init__(self, master):
        super().__init__(master, height=10, bg='black', fg='white')
        self.pack(fill=tk.X)

    def write(self, text):
        self.insert("end", text)
        self.see("end")

    def clear(self):
        self.delete("1.0", "end")
