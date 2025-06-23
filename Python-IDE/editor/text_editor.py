import tkinter as tk
from editor.autocomplete import AutoComplete
from editor.syntax_highlighter import SyntaxHighlighter

class TextEditor(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.text = tk.Text(self, undo=True, wrap='none', font=('Courier', 12))
        self.text.pack(fill=tk.BOTH, expand=1)
        self.syntax = SyntaxHighlighter(self.text)
        self.autocomplete = AutoComplete(self.text)
        self.text.bind("<KeyRelease>", self.update_inline_completion)
        self.text.bind("<Tab>", self.insert_inline_completion)
        self.text.tag_configure("ghost", foreground="grey")
        self.inline_suggestion = ""
        self.text.bind("<Control-space>", self.show_completions)

        self.text.bind("<KeyRelease>", self.syntax.highlight)
        self.text.bind("<F5>", lambda e: master.event_generate("<<RunCode>>"))

    def show_completions(self, event=None):
        index = self.text.index(tk.INSERT)
        suggestions = self.autocomplete.get_suggestions(index)
        if suggestions:
            popup = tk.Toplevel(self)
            popup.wm_overrideredirect(True)
            x, y = self.winfo_pointerxy()
            popup.geometry(f"+{x}+{y}")
            listbox = tk.Listbox(popup)
            listbox.pack()
            for item in suggestions:
                listbox.insert(tk.END, item)

            def insert_selection(e):
                selected = listbox.get(listbox.curselection())
                self.text.insert(tk.INSERT, selected[len(self.text.get("insert linestart", "insert")):])
                popup.destroy()

            listbox.bind("<Double-Button-1>", insert_selection)
            listbox.focus_set()

    def update_inline_completion(self, event=None):
        self.text.tag_remove("ghost", "insert", "insert lineend")
        index = self.text.index(tk.INSERT)
        suggestions = self.autocomplete.get_suggestions(index)
        if suggestions:
            current_line = self.text.get("insert linestart", "insert")
            prefix = current_line.split()[-1] if current_line.strip() else ""
            if prefix and suggestions[0].startswith(prefix) and suggestions[0] != prefix:
                suffix = suggestions[0][len(prefix):]
                self.inline_suggestion = suffix
                self.text.insert(tk.INSERT, suffix)
                self.text.tag_add("ghost", "insert - %dc" % len(suffix), "insert")
                self.text.mark_set("insert", "insert - %dc" % len(suffix))
            else:
                self.inline_suggestion = ""
        else:
            self.inline_suggestion = ""

    def insert_inline_completion(self, event=None):
        if self.inline_suggestion:
            self.text.tag_remove("ghost", "insert", "insert lineend")
            self.text.insert(tk.INSERT, self.inline_suggestion)
            self.inline_suggestion = ""
            return "break"

