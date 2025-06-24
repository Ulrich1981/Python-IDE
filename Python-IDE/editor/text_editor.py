import os
import tkinter as tk
from tkinter import ttk, messagebox
import jedi
import keyword
import re
import threading
from editor.file_manager import load_config, save_config
from executor.package_checker import PackageChecker

PYTHON_KEYWORDS = keyword.kwlist

class TextEditor(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        # Split left for file tree, right for notebook
        self.paned = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned.pack(fill="both", expand=True)

        self.file_tree = ttk.Treeview(self.paned)
        self.file_tree.bind("<<TreeviewOpen>>", self.populate_node)
        self.file_tree.bind("<Double-1>", self.on_file_double_click)
        self.populate_file_tree()

        self.notebook = ttk.Notebook(self.paned)
        self.paned.add(self.file_tree, minsize=180)
        self.paned.add(self.notebook)

        self.paned.pack(fill="both", expand=True)
        self.text_widgets = {}

        self.pkg_checker = PackageChecker()
        self.autocomplete_window = None

        self.add_tab()
        self.load_open_tabs()

        # Bind events for the current text widget on tab change
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        self.bind_events(self.text)

        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="New Tab", command=self.new_tab)
        self.menu.add_command(label="Close Tab", command=self.close_current_tab)
        self.notebook.bind("<Button-3>", self.on_right_click_tab)
        self.menu.add_command(label="Set File Tree Root", command=self.choose_file_tree_root)

    @property
    def text(self):
        current_tab_id = self.notebook.select()
        if not current_tab_id:
            return None
        current_tab = self.nametowidget(current_tab_id)
        return self.text_widgets.get(current_tab)

    def choose_file_tree_root(self):
        from tkinter import filedialog
        directory = filedialog.askdirectory(title="Choose Root Directory")
        if directory:
            self.populate_file_tree(directory)

    def populate_file_tree(self, path="."):
        self.file_tree_root = path  # remember
        self.file_tree.delete(*self.file_tree.get_children())
        root = self.file_tree.insert("", "end", text=os.path.abspath(path), open=True, values=[path])
        self.populate_node_children(root, path)

    def populate_node(self, event):
        node = self.file_tree.focus()
        path = self.get_node_path(node)
        self.populate_node_children(node, path)

    def populate_node_children(self, parent, path):
        self.file_tree.delete(*self.file_tree.get_children(parent))
        try:
            for item in os.listdir(path):
                full = os.path.join(path, item)
                node = self.file_tree.insert(parent, "end", text=item, values=[full])
                if os.path.isdir(full):
                    self.file_tree.insert(node, "end")  # dummy child
        except Exception:
            pass

    def get_node_path(self, node):
        return self.file_tree.item(node, "values")[0]

    def on_file_double_click(self, event):
        item = self.file_tree.focus()
        path = self.get_node_path(item)
        if os.path.isfile(path):
            self.add_tab(path)

    def new_tab(self):
        self.add_tab()

    def close_current_tab(self):
        current_tab_id = self.notebook.select()
        if not current_tab_id:
            return
        if len(self.notebook.tabs()) == 1:
            messagebox.showinfo("Cannot Close Tab", "At least one tab must remain open.")
            return
        frame = self.nametowidget(current_tab_id)
        self.notebook.forget(frame)
        self.text_widgets.pop(frame, None)

    def on_right_click_tab(self, event):
        x, y = event.x, event.y
        elem = self.notebook.identify(x, y)
        if "label" in elem:
            self.menu.tk_popup(event.x_root, event.y_root)

    def add_tab(self, path=None):
        frame = ttk.Frame(self.notebook)
        text_widget = tk.Text(frame, wrap="none", undo=True)
        text_widget.pack(fill="both", expand=True)
        tab_name = os.path.basename(path) if path else "Untitled"
        self.notebook.add(frame, text=tab_name)
        self.text_widgets[frame] = text_widget
        text_widget.path = path

        # Setup tags for syntax highlighting & missing pkg
        self.setup_tags(text_widget)

        if path and os.path.exists(path):
            with open(path, "r") as f:
                content = f.read()
                text_widget.insert("1.0", content)
                self.highlight_syntax(text_widget)

        self.bind_events(text_widget)

    def load_open_tabs(self):
        config = load_config()
        root_dir = config.get("file_tree_root", ".")
        self.populate_file_tree(root_dir)

        files = config.get("open_files", [])
        if not files:
            return
        # Remove initial tab if empty
        if len(self.notebook.tabs()) == 1:
            tab_id = self.notebook.tabs()[0]
            frame = self.nametowidget(tab_id)
            text_widget = self.text_widgets.get(frame)
            if text_widget and not text_widget.get("1.0", "end-1c").strip():
                self.notebook.forget(frame)
                self.text_widgets.pop(frame, None)

        for path in files:
            if os.path.exists(path):
                self.add_tab(path)

        # Select last opened file/tab
        last_file = config.get("last_open_file")
        if last_file and os.path.exists(last_file):
            for tab_id in self.notebook.tabs():
                frame = self.nametowidget(tab_id)
                text_widget = self.text_widgets.get(frame)
                if text_widget and getattr(text_widget, "path", None) == last_file:
                    self.notebook.select(frame)
                    break

    # Update remember_open_tabs to save last open file:
    def remember_open_tabs(self):
        files = []
        for tab_id in self.notebook.tabs():
            frame = self.nametowidget(tab_id)
            text_widget = self.text_widgets.get(frame)
            if text_widget and getattr(text_widget, "path", None):
                files.append(text_widget.path)
        config = load_config()
        config["open_files"] = files
        current_text = self.text
        if current_text and getattr(current_text, "path", None):
            config["last_open_file"] = current_text.path

        root_dir = getattr(self, "file_tree_root", ".")
        config["file_tree_root"] = root_dir
        save_config(config)

    def on_tab_changed(self, event):
        text = self.text
        self.bind_events(text)
        self.highlight_syntax(text)
        self.check_missing_packages(text)

    def bind_events(self, text_widget):
        if not text_widget:
            return
        text_widget.bind("<KeyRelease>", self.on_key_release)
        text_widget.bind("<Tab>", self.handle_tab_completion)
        text_widget.bind("<Button-3>", self.on_right_click)
        text_widget.bind("<Motion>", self.on_mouse_move)

    # ---------- Syntax Highlighting ----------

    def setup_tags(self, text_widget):
        text_widget.tag_configure("keyword", foreground="blue")
        text_widget.tag_configure("string", foreground="orange")
        text_widget.tag_configure("comment", foreground="green")
        text_widget.tag_configure("missing_pkg", background="pink")

    def highlight_syntax(self, text_widget):
        code = text_widget.get("1.0", "end-1c")
        text_widget.tag_remove("keyword", "1.0", "end")
        text_widget.tag_remove("string", "1.0", "end")
        text_widget.tag_remove("comment", "1.0", "end")

        # Basic patterns (could be improved)
        for kw in PYTHON_KEYWORDS:
            start = "1.0"
            while True:
                pos = text_widget.search(r"\b"+kw+r"\b", start, regexp=True, nocase=False, stopindex="end")
                if not pos:
                    break
                end_pos = f"{pos}+{len(kw)}c"
                text_widget.tag_add("keyword", pos, end_pos)
                start = end_pos

        # Strings (single and double quotes)
        for match in re.finditer(r"(['\"])(?:(?=(\\?))\2.)*?\1", code, re.DOTALL):
            start_index = f"1.0+{match.start()}c"
            end_index = f"1.0+{match.end()}c"
            text_widget.tag_add("string", start_index, end_index)

        # Comments
        for match in re.finditer(r"#.*", code):
            start_index = f"1.0+{match.start()}c"
            end_index = f"1.0+{match.end()}c"
            text_widget.tag_add("comment", start_index, end_index)

    # ---------- Autocomplete ----------

    def on_key_release(self, event):
        if event.keysym in ("Return", "Tab", "Escape"):
            self.hide_autocomplete()
            return
        self.highlight_syntax(self.text)
        self.check_missing_packages(self.text)
        self.show_autocomplete()

    def show_autocomplete(self):
        text_widget = self.text
        if not text_widget:
            return
        index = text_widget.index("insert")
        line, col = map(int, index.split('.'))
        code = text_widget.get("1.0", "end-1c")
        script = jedi.Script(code, path=getattr(text_widget, "path", None) or "")

        try:
            completions = script.complete(line, col)
        except Exception:
            completions = []

        if not completions:
            self.hide_autocomplete()
            return

        words = [c.name for c in completions if c.name]

        if not words:
            self.hide_autocomplete()
            return

        if not self.autocomplete_window:
            self.autocomplete_window = tk.Toplevel(self)
            self.autocomplete_window.wm_overrideredirect(True)
            self.listbox = tk.Listbox(self.autocomplete_window, height=6)
            self.listbox.pack()
            self.listbox.bind("<ButtonRelease-1>", self.select_autocomplete)
            self.listbox.bind("<Return>", self.select_autocomplete)
            self.listbox.bind("<Escape>", lambda e: self.hide_autocomplete())
        else:
            self.listbox.delete(0, "end")

        for w in words:
            self.listbox.insert("end", w)

        bbox = text_widget.bbox("insert")
        if not bbox:
            self.hide_autocomplete()
            return
        x, y, width, height = bbox
        x_root = text_widget.winfo_rootx() + x
        y_root = text_widget.winfo_rooty() + y + height

        self.autocomplete_window.wm_geometry(f"+{x_root}+{y_root}")
        self.autocomplete_window.deiconify()
        self.listbox.selection_clear(0, "end")
        self.listbox.selection_set(0)
        self.listbox.activate(0)
        text_widget.focus_set()

    def hide_autocomplete(self):
        if self.autocomplete_window:
            self.autocomplete_window.withdraw()

    def select_autocomplete(self, event=None):
        if not self.autocomplete_window or not self.listbox.curselection():
            return
        selected = self.listbox.get(self.listbox.curselection())
        text_widget = self.text
        if not text_widget:
            return
        index = text_widget.index("insert")
        line, col = map(int, index.split('.'))
        # Delete the current incomplete word
        start = f"{line}.{col}"
        while True:
            char_index = f"{line}.{col-1}"
            if col == 0:
                break
            char = text_widget.get(char_index)
            if not (char.isalnum() or char == "_"):
                break
            col -= 1
        start_word = f"{line}.{col}"
        text_widget.delete(start_word, index)
        text_widget.insert(start_word, selected)
        self.hide_autocomplete()

    def handle_tab_completion(self, event):
        if self.autocomplete_window and self.autocomplete_window.winfo_viewable():
            self.select_autocomplete()
            return "break"
        else:
            # insert tab char
            self.text.insert("insert", " " * 4)
            return "break"

    # ---------- Missing package detection ----------

    def check_missing_packages(self, text_widget):
        if not text_widget:
            return
        # Remove old tags
        text_widget.tag_remove("missing_pkg", "1.0", "end")

        code = text_widget.get("1.0", "end-1c")
        missing = self.pkg_checker.find_missing_packages_with_positions(code)

        for pkg_name, lineno in missing:
            try:
                start = f"{lineno}.0"
                line_text = text_widget.get(start, f"{lineno}.end")
                # Find package name position in line
                idx = line_text.find(pkg_name)
                if idx < 0:
                    continue
                start_index = f"{lineno}.{idx}"
                end_index = f"{lineno}.{idx + len(pkg_name)}"
                text_widget.tag_add("missing_pkg", start_index, end_index)
            except Exception:
                continue

        text_widget.tag_bind("missing_pkg", "<Enter>", self.show_package_tooltip)
        text_widget.tag_bind("missing_pkg", "<Leave>", self.hide_package_tooltip)
        text_widget.tag_bind("missing_pkg", "<Button-1>", self.prompt_install_package)

        self.tooltip = None

    def show_package_tooltip(self, event):
        text_widget = event.widget
        idx = text_widget.index(f"@{event.x},{event.y}")
        tags = text_widget.tag_names(idx)
        if "missing_pkg" not in tags:
            return
        # Get package name under cursor
        start = text_widget.index(f"{idx} wordstart")
        end = text_widget.index(f"{idx} wordend")
        pkg_name = text_widget.get(start, end)

        if hasattr(self, "tooltip") and self.tooltip:
            self.tooltip.destroy()

        self.tooltip = tk.Toplevel(text_widget)
        self.tooltip.wm_overrideredirect(True)
        label = tk.Label(self.tooltip, text=f"Package '{pkg_name}' not installed.\nClick to install.", background="yellow", relief="solid", borderwidth=1)
        label.pack()
        x = event.x_root + 20
        y = event.y_root + 10
        self.tooltip.wm_geometry(f"+{x}+{y}")

    def hide_package_tooltip(self, event):
        if hasattr(self, "tooltip") and self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    def prompt_install_package(self, event):
        text_widget = event.widget
        idx = text_widget.index(f"@{event.x},{event.y}")
        start = text_widget.index(f"{idx} wordstart")
        end = text_widget.index(f"{idx} wordend")
        pkg_name = text_widget.get(start, end)

        answer = messagebox.askyesno("Install Package", f"Package '{pkg_name}' is missing. Install it now?")
        if answer:
            def install():
                self.pkg_checker.install_package(pkg_name)
                messagebox.showinfo("Package Installed", f"Package '{pkg_name}' installed.\nRestart the IDE to reload.")
            threading.Thread(target=install).start()

    # ---------- Right-click menu ----------

    def on_right_click(self, event):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Run Code (F5)", command=self.run_code)
        menu.add_command(label="Save (Ctrl+S)", command=self.save_current_file)
        menu.add_command(label="Open New Tab", command=self.add_tab)
        menu.tk_popup(event.x_root, event.y_root)

    def on_mouse_move(self, event):
        # Could add hover effects here if needed
        pass

    # ---------- Run and Save (to be linked) ----------

    def run_code(self):
        # Placeholder: connect with your runner module
        code = self.text.get("1.0", "end-1c")
        print("Running code:\n", code)

    def save_current_file(self):
        # Placeholder: integrate with your file_manager save_file
        print("Saving current file...")

