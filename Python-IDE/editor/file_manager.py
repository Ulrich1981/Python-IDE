import json
import os
from tkinter import filedialog

CONFIG_PATH = os.path.expanduser("~/.python_ide_config.json")


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)


class FileManager:
    @staticmethod
    def save(text_widget, filename=None):
        config = load_config()
        if not filename:
            initial_dir = config.get("last_dir", os.getcwd())
            file_name = filedialog.asksaveasfilename(
                initialdir=initial_dir,
                defaultextension=".py",
                filetypes=[("Python Files", "*.py")]
            )
        if filename:
            with open(filename, "w") as f:
                f.write(text_widget.get("1.0", "end-1c"))
            config["last_file"] = filename
            config["last_dir"] = os.path.dirname(filename)
            save_config(config)

    @staticmethod
    def load(text_widget):
        config = load_config()
        initial_dir = config.get("last_dir", os.getcwd())
        path = filedialog.askopenfilename(initialdir=initial_dir, filetypes=[("Python Files", "*.py")])
        if path:
            with open(path, "r") as f:
                content = f.read()
                text_widget.delete("1.0", "end")
                text_widget.insert("1.0", content)
            config["last_file"] = path
            config["last_dir"] = os.path.dirname(path)
            save_config(config)
