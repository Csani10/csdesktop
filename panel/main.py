import customtkinter as ctk
import tkinter as tk
from xdg.DesktopEntry import DesktopEntry
import os
from pathlib import Path
import subprocess
from tkinter import messagebox
import time

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
        self.geometry(f"250x300+0+{self.winfo_screenheight() - 300 - 30}")
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


class App(ctk.CTk):
    
    def __init__(self, fg_color = None, **kwargs):
        super().__init__(fg_color=fg_color, **kwargs)
    
        self.title("CsPanel")
        self.overrideredirect(True)
        self.geometry(f"{self.winfo_screenwidth()}x30+0+{self.winfo_screenheight() - 30}")

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
    
    def update_clock(self):
        self.clock.configure(text = time.strftime("%H:%M:%S"))
        self.after(1000, self.update_clock)

    def setup_widgets(self):
        self.menu_btn = ctk.CTkButton(self, text="Menu", width=0, command=self.menu)
        self.menu_btn.pack(side="left", padx=2, pady=2)

        self.clock = ctk.CTkLabel(self, text="")
        self.clock.pack(side="right", padx=2, pady=2)
        self.update_clock()
    
    def get_apps(self):
        for desktop in os.listdir("/usr/share/applications"):
            path = Path.joinpath(Path("/usr/share/applications"), desktop)
            print(path)
            if path.suffix == ".desktop":
                self.apps.append(DesktopEntry(path))
                print(DesktopEntry(path).getExec())

app = App()
app.mainloop()
