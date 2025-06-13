#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from CTkMenuBar import *
from PIL import Image
import cairosvg
import io
import os
from pathlib import Path
import subprocess
import tomllib

csdesktop_config = {}

def bind_mousewheel(widget):
    def _on_mousewheel(event):
        widget._parent_canvas.yview_scroll(-1 * (event.delta // 120), "units")

    # Windows and Mac
    widget.bind_all("<MouseWheel>", _on_mousewheel)

    # Linux (uses Button-4/5)
    widget.bind_all("<Button-4>", lambda e: widget._parent_canvas.yview_scroll(-1, "units"))
    widget.bind_all("<Button-5>", lambda e: widget._parent_canvas.yview_scroll(1, "units"))


def get_sorted_entries(path):
    entries = os.listdir(path)
    return sorted(entries, key=lambda e: (
        not os.path.isdir(os.path.join(path, e)),
        e.lower()
    ))

class App(ctk.CTk):
    def __init__(self, fg_color = None, **kwargs):
        super().__init__(fg_color, **kwargs)

        ctk.set_appearance_mode(csdesktop_config["csdesktop"]["theme"])

        self.title("CsFM")
        self.geometry("800x600")

        self.path_var = ctk.StringVar(self, value=os.getenv("HOME"))

        self.setup_menu()
        self.setup_widgets()
        self.list_files()
    
    def list_files(self):
        for widget in self.file_list.winfo_children():
            widget.destroy()

        current_path = self.path_var.get()

        try:
            entries = get_sorted_entries(current_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not list the folder:\n{str(e)}")
            return

        for entry in entries[:200]:
            full_path = os.path.join(current_path, entry)
            label_text = entry + "/" if os.path.isdir(full_path) else entry

            btn = ctk.CTkButton(
                self.file_list,
                text=label_text,
                anchor="w",
                command=lambda p=full_path: self.chdir(p) if os.path.isdir(p) else self.open(p)
            )
            btn.pack(fill="x", padx=5, pady=1)
        
        self.file_list._parent_canvas.yview_moveto(0.0)



    def chdir(self, path):
        print(path)
        self.path_var.set(path)
        self.list_files()
    
    def dirup(self):
        path = self.path_var.get()
        self.path_var.set(Path(path).parent)
        self.list_files()
    
    def open(self, path):
        subprocess.Popen(["xdg-open", path])
    
    def home(self):
        self.path_var.set(os.getenv("HOME"))
        self.list_files()

    def setup_widgets(self):
        self.top_bar = ctk.CTkFrame(self, height=30)
        self.top_bar.pack(fill="x", side="top")  # no expand

        self.dir_up_btn = ctk.CTkButton(self.top_bar, text="Up", width=30, height=30, command=self.dirup)
        self.dir_up_btn.pack(side="left")

        self.home_dir_btn = ctk.CTkButton(self.top_bar, text="Home", width=30, height=30, command=self.home)
        self.home_dir_btn.pack(side="left")

        self.path_edit = ctk.CTkEntry(self.top_bar, textvariable=self.path_var)
        self.path_edit.pack(side="left", fill="x", expand=True)
        self.path_edit.bind("<Return>", command=lambda ev: self.chdir(self.path_var.get()))

        self.file_list = ctk.CTkScrollableFrame(self)
        self.file_list.pack(fill="both", expand=True)
        bind_mousewheel(self.file_list)
    
    def newdir(self):
        dialog = ctk.CTkInputDialog(text="Directory Name: ", title="New Directory")
        input = dialog.get_input()
        if input:
            os.mkdir(os.path.join(self.path_var.get(), input))
            self.list_files()
    
    def newfile(self):
        dialog = ctk.CTkInputDialog(text="File Name with Extension: ", title="New Empty File")
        input = dialog.get_input()
        if input:
            Path(os.path.join(self.path_var.get(), input)).touch()
            self.list_files()

    def about(self):
        messagebox.showinfo("About", "CsFM by Csani10\nhttps://github.com/Csani10")

    def setup_menu(self):
        self.menu = CTkMenuBar(self)
        self.file_menu = self.menu.add_cascade("File")
        self.help_menu = self.menu.add_cascade("Help")

        self.file_dd = CustomDropdownMenu(self.file_menu)
        self.file_dd.add_option("New Directory", command=self.newdir)
        self.file_dd.add_option("New Empty File", command=self.newfile)
        self.file_dd.add_option("Quit", command=self.quit)

        self.help_dd = CustomDropdownMenu(self.help_menu)
        self.help_dd.add_option("About", command=self.about)

with open(os.getenv("HOME") + "/.config/csdesktop/config.toml", "r") as f:
    csdesktop_config = tomllib.loads(f.read())

app = App()
app.mainloop()
