#!/usr/bin/env python3
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from CTkMenuBar import *
import os
import subprocess
import tomllib
import re

csdesktop_config = {}

class App(ctk.CTk):

    def __init__(self, fg_color = None, **kwargs):
        super().__init__(fg_color, **kwargs)

        ctk.set_appearance_mode(csdesktop_config["csdesktop"]["theme"])

        self.title("CsVol")
        self.geometry("400x200")

        self.setup_menubar()
        self.setup_widgets()

        self.volumes = []
        self.setup_sliders()
    

    def is_mute(self, string):
        if string.lower() == "true":
            return True
        return False

    def about(self):
        messagebox.showinfo("About", "CsVol by Csani10\nhttps://github.com/Csani10")
    
    def change_vol(self, id_):
        for volume in self.volumes:
            if volume["id"] == id_:
                vol = volume["slider"].get()

                subprocess.call(["pamixer", "--sink", str(volume["id"]), "--set-volume", str(int(vol))])
                
    
    def change_mute(self, id_):
        for volume in self.volumes:
            if volume["id"] == id_:
                mute = volume["mutebox"].get()

                if mute == 1:
                    subprocess.call(["pamixer", "--sink", str(volume["id"]), "-m"])
                else:
                    subprocess.call(["pamixer", "--sink", str(volume["id"]), "-u"])
    
    def mute_all(self):
        for volume in self.volumes:
            id_ = volume["id"]
            mutebool = volume["bool"]

            subprocess.call(["pamixer", "--sink", str(id_), "-m"])
            mutebool.set(True)
    
    def unmute_all(self):
        for volume in self.volumes:
            id_ = volume["id"]
            mutebool = volume["bool"]

            subprocess.call(["pamixer", "--sink", str(id_), "-u"])
            mutebool.set(False)


    def setup_sliders(self):
        output = subprocess.getoutput("pamixer --list-sinks")
        output = output.splitlines()[1:]
        print(output)

        pattern = re.compile(r'(\d+)\s+"([^"]+)"\s+"([^"]+)"\s+"([^"]+)"')

        for line in output:
            matched = re.match(pattern, line)

            id_, name, state, friendly_name = matched.groups()
            frame = ctk.CTkFrame(self.volume_list)
            frame.pack(fill="x", expand=True)

            labl = ctk.CTkLabel(frame, text=friendly_name)
            labl.pack()

            volume_int = tk.IntVar(self, value=int(subprocess.getoutput(f"pamixer --sink {id_} --get-volume")))

            slider = ctk.CTkSlider(frame, orientation="horizontal", variable=volume_int, from_=0, to=100, command=lambda ev, id=id_: self.change_vol(id))
            slider.pack(side="left")

            labl2 = ctk.CTkLabel(frame, textvariable=volume_int)
            labl2.pack(side="left")

            volume_bool = tk.BooleanVar(self, value=self.is_mute(subprocess.getoutput(f"pamixer --sink {id_} --get-mute")))

            mute_box = ctk.CTkCheckBox(frame, variable=volume_bool, text="Mute", command=lambda id=id_: self.change_mute(id))
            mute_box.pack(side="right")

            self.volumes.append({
                "id": id_,
                "slider": slider,
                "mutebox": mute_box,
                "int": volume_int,
                "bool": volume_bool
            })
        
        print(self.volumes)
    
    def setup_widgets(self):
        self.volume_list = ctk.CTkScrollableFrame(self)
        self.volume_list.pack(fill="both", expand=True)

    def setup_menubar(self):
        self.menu = CTkMenuBar(self)
        self.volume_menu = self.menu.add_cascade("Volume")
        self.help_menu = self.menu.add_cascade("Help")

        self.volume_dd = CustomDropdownMenu(widget=self.volume_menu)
        self.volume_dd.add_option("Mute All", command=self.mute_all)
        self.volume_dd.add_option("Unmute All", command=self.unmute_all)

        self.help_dd = CustomDropdownMenu(widget=self.help_menu)
        self.help_dd.add_option("About", command=self.about)

with open(os.getenv("HOME") + "/.config/csdesktop/config.toml", "r") as f:
    csdesktop_config = tomllib.loads(f.read())

app = App()
app.mainloop()