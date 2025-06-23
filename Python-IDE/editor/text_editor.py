import tkinter as tk
from editor.autocomplete import AutoComplete
from editor.syntax_highlighter import SyntaxHighlighter
from executor.package_checker import find_missing_packages_with_positions

class TextEditor(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.text = tk.Text(self, undo=True, wrap='none', font=('Courier', 12))
        self.text.pack(fill=tk.BOTH, expand=1)
        self.syntax = SyntaxHighlighter(self.text)
        self.text.bind("<KeyRelease>", self.syntax.highlight)
        self.autocomplete = AutoComplete(self.text)
        self.text.bind("<KeyRelease>", self.update_inline_completion)
        self.text.bind("<Tab>", self.insert_inline_completion)
        self.text.tag_configure("ghost", foreground="grey")
        self.inline_suggestion = ""
        self.text.bind("<Control-space>", self.show_completions)
        self.text.bind("<F5>", lambda e: master.event_generate("<<RunCode>>"))

        self.schedule_package_check()

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
            word = re.split(r'\W', current_line)[-1]
            match = next((s for s in suggestions if s.startswith(word) and s != word), "")
            if match:
                suffix = match[len(word):]
                self.inline_suggestion = suffix
                self.text.insert(tk.INSERT, suffix)
                self.text.tag_add("ghost", f"insert - {len(suffix)}c", "insert")
                self.text.mark_set("insert", f"insert - {len(suffix)}c")
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

    def check_missing_packages(self):
        code = self.text.get("1.0", "end-1c")
        self.text.tag_remove("missing_pkg", "1.0", "end")
        self.text.tag_configure("missing_pkg", underline=True, foreground="red")

        missing = find_missing_packages_with_positions(code)
        for pkg, lineno in missing:
            line_start = f"{lineno}.0"
            line_text = self.text.get(line_start, f"{lineno}.end")
            start_index = line_text.find(pkg)
            if start_index != -1:
                start = f"{lineno}.{start_index}"
                end = f"{lineno}.{start_index + len(pkg)}"
                self.text.tag_add("missing_pkg", start, end)

        # bind tooltip
        self.text.tag_bind("missing_pkg", "<Enter>", self.show_install_tooltip)
        self.text.tag_bind("missing_pkg", "<Leave>", self.hide_tooltip)
        self.text.tag_bind("missing_pkg", "<Button-1>", self.install_package_prompt)

    def show_install_tooltip(self, event):
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()
        self.tooltip = tk.Toplevel(self)
        self.tooltip.wm_overrideredirect(True)
        x = event.x_root + 10
        y = event.y_root + 10
        self.tooltip.geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text="Click to install package", bg="yellow", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event):
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()
            del self.tooltip

    def install_package_prompt(self, event):
        index = self.text.index(f"@{event.x},{event.y}")
        tags = self.text.tag_names(index)
        if "missing_pkg" in tags:
            # find package name under mouse
            for tag_range in self.text.tag_ranges("missing_pkg"):
                start = tag_range.string
                if self.text.compare(start, "<=", index) and self.text.compare(index, "<", tag_range):
                    pkg_name = self.text.get(tag_range, f"{tag_range} + {len(pkg_name)}c")
                    break
            else:
                # fallback: get word at index
                pkg_name = self.text.get(f"{index} wordstart", f"{index} wordend")

            import tkinter.messagebox as msgbox
            if msgbox.askyesno("Install package", f"Do you want to install '{pkg_name}'?"):
                import subprocess, sys
                subprocess.Popen([sys.executable, "-m", "pip", "install", pkg_name])
                msgbox.showinfo("Installing", f"Installing '{pkg_name}' in background.")

    def schedule_package_check(self):
        self.check_missing_packages()
        self.after(2000, self.schedule_package_check)
