import jedi

class AutoComplete:
    def __init__(self, text_widget):
        self.text = text_widget

    def get_suggestions(self, cursor_index):
        try:
            code = self.text.get("1.0", "end-1c")
            line, col = map(int, cursor_index.split("."))
            script = jedi.Script(code, path="user_code.py")
            completions = script.complete(line, col)
            return [c.name for c in completions]
        except Exception:
            return []
