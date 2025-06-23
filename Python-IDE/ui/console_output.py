import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO
import matplotlib.pyplot as plt

class ConsoleOutput(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.text = tk.Text(self, height=10, bg='black', fg='white')
        self.text.pack(fill=tk.BOTH, expand=True)
        self.text.configure(state='disabled')

        self.image_refs = []

    def write(self, content):
        self.text.configure(state='normal')
        self.text.insert(tk.END, content)
        self.text.see(tk.END)
        self.text.configure(state='disabled')

    def clear(self):
        self.text.configure(state='normal')
        self.text.delete("1.0", tk.END)
        self.text.configure(state='disabled')
        self.image_refs.clear()

    def display_plot(self):
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        image = Image.open(buf)
        photo = ImageTk.PhotoImage(image)
        self.image_refs.append(photo)  # Keep reference to prevent GC

        self.text.image_create(tk.END, image=photo)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
