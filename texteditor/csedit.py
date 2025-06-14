#!/usr/bin/env python3
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from CTkMenuBar import *
import os
import tomllib
import sys

csdesktop_config = {}

class App(ctk.CTk):

    def __init__(self, file = "", fg_color = None, **kwargs):
        super().__init__(fg_color, **kwargs)

        ctk.set_appearance_mode(csdesktop_config["csdesktop"]["theme"])

        self.title("CsEdit")
        self.geometry("800x600")

        self.setup_menubar()
        self.setup_widgets()

        self.file = file
        self.read_file()

        self.filetypes = (
            ("Text files", "*.txt"),
            ("All files", "*.*")
        )
    
    def read_file(self):
        if self.file:
            with open(self.file, "r") as f:
                self.text_edit.delete("0.0", "end")
                self.text_edit.insert("0.0", f.read())

    def open_file(self):
        file = ctk.filedialog.askopenfilename(defaultextension=".txt", filetypes=self.filetypes)
        if file:
            self.file = file
            self.read_file()
    
    def save_file(self, new):
        if new:
            file = ctk.filedialog.asksaveasfilename(defaultextension=".txt", filetypes=self.filetypes)
            try:
                with open(file, "w+") as f:
                    f.truncate()
                    f.write(self.text_edit.get("0.0", "end"))
                self.file = file
            except:
                tk.Message(self, text="Could not save file")
        else:
            if not self.file == "":
                try:
                    with open(self.file, "w+") as f:
                        f.truncate()
                        f.write(self.text_edit.get("0.0", "end"))
                except: 
                    tk.Message(self, text="Could not save file")
            else:
                file = ctk.filedialog.asksaveasfilename(defaultextension=".txt", filetypes=self.filetypes)
                try:
                    with open(file, "w+") as f:
                        f.truncate()
                        f.write(self.text_edit.get("0.0", "end"))
                    self.file = file
                except:
                    tk.Message(self, text="Could not save file")

    def new_file(self):
        self.text_edit.delete("0.0", "end")
        self.file = ""

    def select_all(self, _ev):
        self.text_edit.tag_add("sel", "1.0", "end-1c")
        return "break"

    def copy(self):
        self.clipboard_clear()
        self.clipboard_append(self.text_edit.get("sel.first", "sel.last"))
        return "break"

    def cut(self):
        self.copy()
        self.text_edit.delete("sel.first", "sel.last")
        return "break"
    
    def paste(self):
        self.text_edit.insert("insert", self.clipboard_get())
        return "break"

    def about(self):
        messagebox.showinfo("About", "CsEdit by Csani10\nhttps://github.com/Csani10")

    def setup_widgets(self):
        self.text_edit = ctk.CTkTextbox(self)
        self.text_edit.bind("<Control-Key-a>", command=self.select_all)
        self.text_edit.bind("<Control-Key-A>", command=self.select_all)
        self.text_edit.bind("<Control-Key-c>", command=lambda ev: self.copy)
        self.text_edit.bind("<Control-Key-C>", command=lambda ev: self.copy)
        self.text_edit.bind("<Control-Key-v>", command=lambda ev: self.paste)
        self.text_edit.bind("<Control-Key-V>", command=lambda ev: self.paste)
        self.text_edit.bind("<Control-Key-x>", command=lambda ev: self.cut)
        self.text_edit.bind("<Control-Key-X>", command=lambda ev: self.cut)
        self.text_edit.pack(fill="both", anchor="center", expand=True)

    def setup_menubar(self):
        self.menu = CTkMenuBar(self)
        self.file_menu = self.menu.add_cascade("File")
        self.edit_menu = self.menu.add_cascade("Edit")
        self.help_menu = self.menu.add_cascade("Help")

        self.file_dd = CustomDropdownMenu(widget=self.file_menu)
        self.file_dd.add_option("New File", command=self.new_file)
        self.file_dd.add_option("Open File", command=self.open_file)
        self.file_dd.add_option("Save File", command=lambda: self.save_file(False))
        self.file_dd.add_option("Save as", command=lambda: self.save_file(True))

        self.edit_dd = CustomDropdownMenu(widget=self.edit_menu)
        self.edit_dd.add_option("Copy", command=self.copy)
        self.edit_dd.add_option("Paste", command=self.paste)
        self.edit_dd.add_option("Cut", command=self.cut)

        self.help_dd = CustomDropdownMenu(widget=self.help_menu)
        self.help_dd.add_option("About", command=self.about)

        self.configure(menu=self.menu)

with open(os.getenv("HOME") + "/.config/csdesktop/config.toml", "r") as f:
    csdesktop_config = tomllib.loads(f.read())

if len(sys.argv) > 1:
    app = App(file=sys.argv[1])
else:
    app = App()

app.mainloop()
