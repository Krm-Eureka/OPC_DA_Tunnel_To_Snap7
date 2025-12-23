import customtkinter as ctk
import queue
from core.opc_client import OPCClient
from core.plc_client import PLCClient
from core.mapper import Mapper
from core.logger import logger
from config import settings

ctk.set_appearance_mode("dark")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1000x600")

        self.sidebar = Sidebar(self, self.show_page)
        self.sidebar.pack(side="left", fill="y")

        self.container = ctk.CTkFrame(self)
        self.container.pack(expand=True, fill="both")

        self.pages = {
            "config": ConfigPage(self.container),
            "monitor": MonitorPage(self.container),
            "log": LogPage(self.container),
        }

        self.show_page("config")

        self.after(100, self.gui_update_loop)

    def show_page(self, name):
        for p in self.pages.values():
            p.pack_forget()
        self.pages[name].pack(expand=True, fill="both")

    def gui_update_loop(self):
        while not data_queue.empty():
            data = data_queue.get()
            self.pages["monitor"].update_data(data)

        self.after(100, self.gui_update_loop)
