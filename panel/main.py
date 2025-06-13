import customtkinter as ctk
import tkinter as tk
from xdg.DesktopEntry import DesktopEntry
import os
from pathlib import Path
import subprocess
from tkinter import messagebox
import time
import tomllib
import re

DASH_SPLIT_REGEX = re.compile(r'\s*[-–—]\s*')

config = {}

def bind_mousewheel(widget):
    def _on_mousewheel(event):
        widget._parent_canvas.yview_scroll(-1 * (event.delta // 120), "units")

    # Windows and Mac
    widget.bind_all("<MouseWheel>", _on_mousewheel)

    # Linux (uses Button-4/5)
    widget.bind_all("<Button-4>", lambda e: widget._parent_canvas.yview_scroll(-1, "units"))
    widget.bind_all("<Button-5>", lambda e: widget._parent_canvas.yview_scroll(1, "units"))

class StartMenu(ctk.CTkToplevel):

    def __init__(self, apps, fg_color = None, **kwargs):
        super().__init__(fg_color=fg_color, **kwargs)
        
        self.apps = apps
        self.app_index = 0
        
        self.title("CsStart")
        self.overrideredirect(True)
        self.geometry(f"250x300+0+{self.winfo_screenheight() - 300 - config["panel"]["height"]}")
        self.setup_widgets()
    
    def app(self, idx):
        print(self.apps[idx])
        try:
            subprocess.Popen(self.apps[idx].getExec().split(" "))
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", e)

    def setup_widgets(self):
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)
        
        self.tab_view = ctk.CTkTabview(self.main_frame)
        self.tab_view.pack(fill="both", expand=True)             
                
        self.tab_view.add("Menu")
        self.tab_view.add("Apps")
        
        self.menu_tab = self.tab_view.tab("Menu")
        self.apps_tab = self.tab_view.tab("Apps")

        self.apps_view = ctk.CTkScrollableFrame(self.apps_tab)
        self.apps_view.pack(fill="both", expand=True)
        bind_mousewheel(self.apps_view)

        self.menu_view = ctk.CTkScrollableFrame(self.menu_tab)
        self.menu_view.pack(fill="both", expand=True)
        bind_mousewheel(self.menu_view)

        self.batch_add_apps()
        
    
    def batch_add_apps(self, batch_size=10):
        for _ in range(batch_size):
            if self.app_index >= len(self.apps):
                return
            app = self.apps[self.app_index]
            btn = ctk.CTkButton(
                self.apps_view,
                text=app.getName(),
                command=lambda idx=self.app_index: self.app(idx)
            )
            btn.pack(fill="x", padx=5, pady=2)
            self.app_index += 1

        self.after(10, self.batch_add_apps)

class Tray(ctk.CTkFrame):

    def __init__(self, master, width = 200, height = 200, corner_radius = None, border_width = None, bg_color = "transparent", fg_color = None, border_color = None, background_corner_colors = None, overwrite_preferred_drawing_method = None, **kwargs):
        super().__init__(master, width, height, corner_radius, border_width, bg_color, fg_color, border_color, background_corner_colors, overwrite_preferred_drawing_method, **kwargs)

        self.after(100, self.update_tray)

        self.windows = []
    
    def switch_win(self, id):
        subprocess.Popen(["wmctrl", "-i", "-a", id])

    def update_tray(self):
        output = subprocess.check_output(["wmctrl", "-l"], text=True)

        windows = []
        pattern = re.compile(r'^(0x[0-9a-fA-F]+)\s+(\d+)\s+([^\s]+)\s+(.*)$')

        for line in output.strip().splitlines():
            match = pattern.match(line)
            if match:
                win_id, desktop, host, title = match.groups()

                parts = DASH_SPLIT_REGEX.split(title)
                if len(parts) > 1:
                    title = parts[-1].strip()


                windows.append({
                    "id": win_id,
                    "desktop": desktop,
                    "host": host,
                    "title": title
                })

        if not windows == self.windows:
            for child in self.winfo_children():
                child.destroy()

            for window in windows:
                print(window["title"], window["id"])
                label = ctk.CTkButton(self, width=0, text=window["title"], command=lambda id=window["id"]: self.switch_win(id))
                label.pack(side="left", padx=2, pady=5)
            
            self.windows = windows
        
        self.after(100, self.update_tray)


class App(ctk.CTk):
    
    def __init__(self, fg_color = None, **kwargs):
        super().__init__(fg_color=fg_color, **kwargs)
    
        self.title("CsPanel")
        self.overrideredirect(True)
        self.geometry(f"{self.winfo_screenwidth()}x{config["panel"]["height"]}+0+{self.winfo_screenheight() - config["panel"]["height"]}")

        self.setup_widgets()
        self.start_menu = None
        self.apps = []

        self.get_apps()
    
    def menu(self):
        if self.start_menu == None or not self.start_menu.winfo_exists():
            self.start_menu = StartMenu(self.apps)
        else:
            self.start_menu.destroy()
            self.start_menu = None
    
    def update_clock(self, widget, format):
        widget.configure(text = time.strftime(format))
        self.after(1000, lambda wg=widget, format=format: self.update_clock(wg, format))

    def setup_widgets(self):
        for widget in config["widgets"]:
            if widget["type"] == "menu":
                print(widget)
                menu = ctk.CTkButton(self, text=widget["text"], width=0, command=self.menu)
                menu.pack(side=widget["align"], padx=2, pady=2)
            elif widget["type"] == "clock":
                clock = ctk.CTkLabel(self, text="")
                clock.pack(side=widget["align"], padx=2, pady=2)
                self.update_clock(clock, widget["format"])
            elif widget["type"] == "tray":
                tray = Tray(self)
                tray.pack(fill="x", side=widget["align"])
    
    def get_apps(self):
        for desktop in os.listdir("/usr/share/applications"):
            path = Path.joinpath(Path("/usr/share/applications"), desktop)
            if path.suffix == ".desktop":
                if not DesktopEntry(path).getHidden():
                    self.apps.append(DesktopEntry(path))
        
        self.apps = sorted(self.apps, key=lambda entry: entry.getName())

with open("config.toml", "r") as f:
    config = tomllib.loads(f.read())
    print(config)

app = App()
app.mainloop()
