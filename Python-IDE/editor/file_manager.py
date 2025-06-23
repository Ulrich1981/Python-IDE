from tkinter import filedialog

class FileManager:
    @staticmethod
    def save(text_widget, filename=None):
        if not filename:
            filename = filedialog.asksaveasfilename(defaultextension=".py")
        if filename:
            with open(filename, 'w') as f:
                f.write(text_widget.get("1.0", "end-1c"))
        return filename

    @staticmethod
    def load(text_widget):
        filename = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if filename:
            with open(filename, 'r') as f:
                text_widget.delete("1.0", "end")
                text_widget.insert("1.0", f.read())
        return filename
