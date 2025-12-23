import customtkinter as ctk
from tkinter import filedialog
import xml.etree.ElementTree as ET
import os
from core.state import state

ctk.set_appearance_mode("Dark")  # บังคับ Dark Theme
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("KONE OPC DA Tunnel")
        self.geometry("1000x700")
        
        # Layout หลัก: 2 คอลัมน์ (Sidebar ซ้าย, Content ขวา)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="OPC TUNNEL", font=("Roboto", 24, "bold"))
        self.logo_label.pack(pady=30)

        # Buttons Menu
        self.btn_monitor = self.create_sidebar_btn("Monitor", "monitor")
        self.btn_config = self.create_sidebar_btn("Config", "config")
        self.btn_logs = self.create_sidebar_btn("Logs", "logs")
        
        # Simulation Switch
        self.sim_switch = ctk.CTkSwitch(self.sidebar, text="Simulation Mode", command=self.toggle_sim)
        self.sim_switch.pack(side="bottom", pady=20, padx=20)

        # --- Main Content Area ---
        self.container = ctk.CTkFrame(self)
        self.container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        self.frames = {}
        self.create_monitor_page()
        self.create_config_page()
        self.create_logs_page()

        self.show_frame("config") # เริ่มต้นที่หน้า Config
        self.update_gui_loop()

    def create_sidebar_btn(self, text, frame_name):
        btn = ctk.CTkButton(self.sidebar, text=text, height=40, corner_radius=5, 
                            fg_color="transparent", border_width=1,
                            command=lambda: self.show_frame(frame_name))
        btn.pack(pady=5, padx=10, fill="x")
        return btn

    def show_frame(self, name):
        for frame in self.frames.values():
            frame.grid_forget()
        self.frames[name].grid(row=0, column=0, sticky="nsew")

    # ================= PAGES =================

    def create_monitor_page(self):
        frame = ctk.CTkFrame(self.container)
        self.frames["monitor"] = frame
        frame.grid_columnconfigure(0, weight=1)

        # Header Status
        status_frame = ctk.CTkFrame(frame, height=50)
        status_frame.pack(fill="x", padx=10, pady=10)
        
        self.lbl_status_opc = ctk.CTkLabel(status_frame, text="OPC: Disconnected", text_color="red", font=("Arial", 16, "bold"))
        self.lbl_status_opc.pack(side="left", padx=20)
        
        self.lbl_status_plc = ctk.CTkLabel(status_frame, text="PLC: Disconnected", text_color="red", font=("Arial", 16, "bold"))
        self.lbl_status_plc.pack(side="right", padx=20)

        # Data Display
        self.monitor_textbox = ctk.CTkTextbox(frame, font=("Consolas", 14))
        self.monitor_textbox.pack(fill="both", expand=True, padx=10, pady=10)

    def create_config_page(self):
        frame = ctk.CTkFrame(self.container)
        self.frames["config"] = frame
        
        # --- PLC Settings Group ---
        grp_plc = ctk.CTkFrame(frame)
        grp_plc.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(grp_plc, text="PLC Settings (Snap7)", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=5)
        
        self.ent_plc_ip = self.create_input(grp_plc, "PLC IP:", state.plc_ip)
        
        row_rack = ctk.CTkFrame(grp_plc, fg_color="transparent")
        row_rack.pack(fill="x", padx=10)
        self.ent_plc_rack = self.create_input(row_rack, "Rack:", str(state.plc_rack), side="left")
        self.ent_plc_slot = self.create_input(row_rack, "Slot:", str(state.plc_slot), side="right")

        # --- OPC Settings Group ---
        grp_opc = ctk.CTkFrame(frame)
        grp_opc.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(grp_opc, text="OPC Settings (PyWin32)", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=5)
        
        self.ent_opc_host = self.create_input(grp_opc, "OPC Host (Computer Name/IP):", state.opc_host)
        self.ent_opc_server = self.create_input(grp_opc, "OPC Server Name:", state.opc_server_name)

        # --- Tag Import Group ---
        grp_tag = ctk.CTkFrame(frame)
        grp_tag.pack(fill="both", expand=True, padx=10, pady=10)
        
        head_frame = ctk.CTkFrame(grp_tag, fg_color="transparent")
        head_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(head_frame, text="Tag List", font=("Arial", 16, "bold")).pack(side="left")
        
        btn_import = ctk.CTkButton(head_frame, text="Import XML", fg_color="#E0a800", text_color="black", command=self.import_xml)
        btn_import.pack(side="right")

        self.tag_preview = ctk.CTkTextbox(grp_tag, height=150)
        self.tag_preview.pack(fill="both", expand=True, padx=10, pady=5)
        self.refresh_tag_preview()

        # --- Action Buttons ---
        btn_save = ctk.CTkButton(frame, text="SAVE & APPLY CONFIG", height=50, fg_color="green", command=self.save_config)
        btn_save.pack(fill="x", padx=20, pady=20)

    def create_logs_page(self):
        frame = ctk.CTkFrame(self.container)
        self.frames["logs"] = frame
        self.log_textbox = ctk.CTkTextbox(frame, font=("Consolas", 12))
        self.log_textbox.pack(fill="both", expand=True, padx=10, pady=10)

    # ================= LOGIC =================
    
    def create_input(self, parent, label_text, default_val, side="top"):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=5, side=side)
        ctk.CTkLabel(frame, text=label_text, width=150, anchor="w").pack(side="left")
        entry = ctk.CTkEntry(frame)
        entry.insert(0, default_val)
        entry.pack(side="right", fill="x", expand=True)
        return entry

    def import_xml(self):
        """อ่านไฟล์ XML และดึงค่าจาก tag <Item>"""
        file_path = filedialog.askopenfilename(filetypes=[("XML Files", "*.xml")])
        if not file_path:
            return

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # ค้นหา <Item> ทั้งหมดในไฟล์ (XPath .//Item)
            items = root.findall(".//Item")
            
            new_tags = []
            for item in items:
                if item.text:
                    tag_name = item.text.strip() # ตัดช่องว่างหน้าหลัง
                    if tag_name:
                        new_tags.append(tag_name)
            
            if new_tags:
                state.opc_tag_list = new_tags
                self.refresh_tag_preview()
                state.log("CONFIG", f"Imported {len(new_tags)} tags from {os.path.basename(file_path)}")
            else:
                state.log("CONFIG", "No tags found in XML")
                
        except Exception as e:
            state.log("CONFIG", f"Import XML Error: {e}")

    def refresh_tag_preview(self):
        self.tag_preview.delete("0.0", "end")
        for i, tag in enumerate(state.opc_tag_list, 1):
            self.tag_preview.insert("end", f"{i}. {tag}\n")

    def save_config(self):
        """บันทึกค่าลงตัวแปร state"""
        state.plc_ip = self.ent_plc_ip.get()
        state.plc_rack = int(self.ent_plc_rack.get())
        state.plc_slot = int(self.ent_plc_slot.get())
        
        state.opc_host = self.ent_opc_host.get()
        state.opc_server_name = self.ent_opc_server.get()
        
        state.log("GUI", "Configuration Saved. Please restart connections if needed.")
        # Optional: อาจจะสั่งให้ Worker reconnect ตรงนี้ได้

    def toggle_sim(self):
        state.simulation_mode = bool(self.sim_switch.get())
        state.log("GUI", f"Simulation Mode: {state.simulation_mode}")

    def update_gui_loop(self):
        # Update Status Labels
        self.lbl_status_opc.configure(
            text=f"OPC: {'Connected' if state.opc_connected else 'Disconnected'}",
            text_color="#00FF00" if state.opc_connected else "#FF0000"
        )
        self.lbl_status_plc.configure(
            text=f"PLC: {'Connected' if state.plc_connected else 'Disconnected'}",
            text_color="#00FF00" if state.plc_connected else "#FF0000"
        )

        # Update Monitor Page (ถ้าเปิดอยู่)
        if self.frames["monitor"].winfo_viewable():
            text = "--- OPC LIVE VALUES ---\n"
            with state.data_lock:
                for k, v in state.opc_values.items():
                    text += f"{k:<50} : {v}\n"
                
                text += "\n--- PLC DATA ---\n"
                for k, v in state.plc_data.items():
                    text += f"{k:<20} : {v}\n"
            
            self.monitor_textbox.delete("0.0", "end")
            self.monitor_textbox.insert("0.0", text)

        # Update Logs (ถ้าเปิดอยู่)
        if self.frames["logs"].winfo_viewable():
            logs = state.get_logs()
            self.log_textbox.delete("0.0", "end")
            self.log_textbox.insert("0.0", "\n".join(logs))

        self.after(500, self.update_gui_loop)