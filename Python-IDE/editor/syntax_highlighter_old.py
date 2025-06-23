import keyword
import tkinter as tk

class SyntaxHighlighter:
    def __init__(self, text_widget):
        self.text = text_widget
        self.text.tag_config("keyword", foreground="blue")

    def highlight(self, event=None):
        self.text.tag_remove("keyword", "1.0", "end")
        for word in keyword.kwlist:
            idx = "1.0"
            while True:
                idx = self.text.search(rf"\b{word}\b", idx, nocase=0, stopindex="end", regexp=True)
                if not idx:
                    break
                end = f"{idx}+{len(word)}c"
                self.text.tag_add("keyword", idx, end)
                idx = end
