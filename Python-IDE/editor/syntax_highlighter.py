import keyword
import re

class SyntaxHighlighter:
    def __init__(self, text_widget):
        self.text = text_widget
        self.text.tag_configure("keyword", foreground="blue")

    def highlight(self, event=None):
        content = self.text.get("1.0", "end-1c")
        self.text.tag_remove("keyword", "1.0", "end")

        for word in keyword.kwlist:
            for match in re.finditer(rf'\b{word}\b', content):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.text.tag_add("keyword", start, end)
