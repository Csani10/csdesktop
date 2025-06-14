#!/usr/bin/env python3
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
csdesktop_config = {}
logsfile = open(os.getenv("HOME") + "/cspanel.log", "w+")
logsfile.truncate()
logsfile.flush()

def log(log):
    print(log)
    logsfile.write(str(log) + "\n")
    logsfile.flush()

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
    
    def logout(self):
        subprocess.call(["openbox", "--exit"])
    
    def reboot(self):
        subprocess.call(["systemctl", "reboot"])
    
    def shutdown(self):
        subprocess.call(["systemctl", "poweroff"])

    def app(self, idx):
        log(self.apps[idx])
        try:
            log(self.apps[idx].getExec().strip("%u%U%f%F%i%c%k").replace(" ", "#").split("#"))
            exc = []
            for i in self.apps[idx].getExec().strip("%u%U%f%F%i%c%k").replace(" ", "#").split("#"):
                if i == " " or i == "":
                    continue
                else:
                    exc.append(i)
            subprocess.Popen(exc)
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

        self.logout_button = ctk.CTkButton(self.menu_view, text="Logout", command=self.logout)
        self.logout_button.pack(fill="x", padx=2, pady=2)

        self.reboot_button = ctk.CTkButton(self.menu_view, text="Reboot", command=self.reboot)
        self.reboot_button.pack(fill="x", padx=2, pady=2)

        self.shutdown_button = ctk.CTkButton(self.menu_view, text="Shutdown", command=self.shutdown)
        self.shutdown_button.pack(fill="x", padx=2, pady=2)

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

        self.buttons = []
    
    def switch_win(self, id):
        subprocess.Popen(["wmctrl", "-i", "-a", id])

        for btn in self.buttons:
            if btn["id"] == id:
                btn["button"].configure(state="disabled")
            else:
                btn["button"].configure(state="normal")

    def update_tray(self):
        output = subprocess.check_output(["wmctrl", "-l"], text=True)

        windows = []
        pattern = re.compile(r'^(0x[0-9a-fA-F]+)\s+(\d+)\s+([^\s]+)\s+(.*)$')

        self.active_win = subprocess.check_output(["xprop", "-root", "_NET_ACTIVE_WINDOW"], text=True)

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

            self.buttons.clear()

            for window in windows:
                log(window["title"], window["id"])
                label = ctk.CTkButton(self, width=0, text=window["title"], command=lambda id=window["id"]: self.switch_win(id))
                label.pack(side="left", padx=2, pady=5)
                self.buttons.append({
                    "button": label,
                    "id": window["id"]
                })
            
            self.windows = windows
        for btn in self.buttons:
            log(btn["id"])
            if btn["id"] == "0x{:08x}".format(int(self.active_win.strip("\n").split(" ")[4], 16)):
                btn["button"].configure(state="disabled")
            else:
                btn["button"].configure(state="normal")

        self.after(100, self.update_tray)


class App(ctk.CTk):
    
    def __init__(self, fg_color = None, **kwargs):
        super().__init__(fg_color=fg_color, **kwargs)
    
        if "theme" in config["panel"].keys():
            ctk.set_appearance_mode(config["panel"]["theme"])
        else:
            ctk.set_appearance_mode(csdesktop_config["csdesktop"]["theme"])

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

    def cmd(self, cmd):
        subprocess.Popen(cmd.split(" "))

    def setup_widgets(self):
        for widget in config["widgets"]:
            if widget["type"] == "menu":
                log(widget)
                menu = ctk.CTkButton(self, text=widget["text"], width=0, command=self.menu)
                menu.pack(side=widget["align"], padx=2, pady=2)
            elif widget["type"] == "clock":
                clock = ctk.CTkLabel(self, text="")
                clock.pack(side=widget["align"], padx=2, pady=2)
                self.update_clock(clock, widget["format"])
            elif widget["type"] == "tray":
                tray = Tray(self)
                tray.pack(fill="x", side=widget["align"])
            elif widget["type"] == "cmdbtn":
                cmdbtn = ctk.CTkButton(self, text=widget["text"], command=lambda cmd=widget["command"]: self.cmd(cmd), width=0)
                cmdbtn.pack(side=widget["align"], padx=2, pady=2)
    
    def get_apps(self):
        for desktop in os.listdir("/usr/share/applications"):
            path = Path.joinpath(Path("/usr/share/applications"), desktop)
            if path.suffix == ".desktop":
                if not DesktopEntry(path).getHidden():
                    self.apps.append(DesktopEntry(path))
        
        for desktop in os.listdir(os.getenv("HOME") + "/.local/share/applications"):
            path = Path.joinpath(Path(os.getenv("HOME") + "/.local/share/applications"), desktop)
            if path.suffix == ".desktop":
                if not DesktopEntry(path).getHidden():
                    if DesktopEntry(path) in self.apps:
                        continue
                    self.apps.append(DesktopEntry(path))
        
        self.apps = sorted(self.apps, key=lambda entry: entry.getName())

with open(os.getenv("HOME") + "/.config/csdesktop/panel.toml", "r") as f:
    config = tomllib.loads(f.read())

with open(os.getenv("HOME") + "/.config/csdesktop/config.toml", "r") as f:
    csdesktop_config = tomllib.loads(f.read())

app = App()
app.mainloop()
logsfile.close()




