from tkinter import Menu
from editor.file_manager import FileManager

def setup_menu(root, editor, runner):
    menubar = Menu(root)

    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Open", command=lambda: FileManager.load(editor.text))
    filemenu.add_command(label="Save", command=lambda: FileManager.save(editor.text))
    filemenu.add_command(label="Save As", command=lambda: FileManager.save(editor.text, None))
    menubar.add_cascade(label="File", menu=filemenu)

    runmenu = Menu(menubar, tearoff=0)
    runmenu.add_command(label="Run", command=runner.run_code)
    menubar.add_cascade(label="Run", menu=runmenu)

    root.config(menu=menubar)
