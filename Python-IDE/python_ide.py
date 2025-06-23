import tkinter as tk
from editor.text_editor import TextEditor
from ui.console_output import ConsoleOutput
from ui.menu_bar import setup_menu
from executor.code_runner import CodeRunner
from check_for_updates import check_for_updates

def main():
    root = tk.Tk()
    root.title("Modular Python IDE")

    editor = TextEditor(root)
    editor.pack(fill=tk.BOTH, expand=1)

    console = ConsoleOutput(root)
    console.pack(fill=tk.X)

    runner = CodeRunner(editor, console)
    setup_menu(root, editor, runner)

    root.mainloop()

if __name__ == "__main__":
    check_for_updates()
    main()
