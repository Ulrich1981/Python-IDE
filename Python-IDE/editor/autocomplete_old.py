import jedi

class AutoComplete:
    def __init__(self, text_widget):
        self.text = text_widget

    def get_suggestions(self, cursor_index):
        code = self.text.get("1.0", "end-1c")
        script = jedi.Script(code, *map(int, cursor_index.split('.')))
        try:
            return [c.name for c in script.complete()]
        except:
            return []
