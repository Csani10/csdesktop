import customtkinter as ctk
import tkinter as tk

class StartMenu(ctk.CTkToplevel):

    def __init__(self, fg_color = None, **kwargs):
        super().__init__(fg_color=fg_color, **kwargs)
        
        self.title("CsStart")
        self.overrideredirect(True)
        self.geometry(f"250x300+0+{self.winfo_screenheight() - 300 - 30}")
        self.setup_widgets()
    
    def setup_widgets(self):
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)
        
        self.tab_view = ctk.CTkTabview(self.main_frame)
        self.tab_view.pack(fill="both", expand=True)             
                
        self.tab_view.add("Menu")
        self.tab_view.add("Apps")
        
        self.menu_tab = self.tab_view.tab("Menu")
        self.apps_tab = self.tab_view.tab("Apps")
        
        
class App(ctk.CTk):
    
    def __init__(self, fg_color = None, **kwargs):
        super().__init__(fg_color=fg_color, **kwargs)
    
        self.title("CsPanel")
        self.overrideredirect(True)
        self.geometry(f"{self.winfo_screenwidth()}x30+0+{self.winfo_screenheight() - 30}")

        self.setup_widgets()
        self.start_menu = None
    
    def menu(self):
        if self.start_menu == None:
            self.start_menu = StartMenu()
        else:
            self.start_menu.destroy()
            self.start_menu = None
    
    def setup_widgets(self):
        self.menu_btn = ctk.CTkButton(self, text="Menu", width=0, command=self.menu)
        self.menu_btn.pack(side="left", padx=2, pady=2)

app = App()
app.mainloop()