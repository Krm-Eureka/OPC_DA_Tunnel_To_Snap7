import threading
from datetime import datetime

class AppState:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(AppState, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.data_lock = threading.Lock()
        
        # --- Config Default ---
        self.simulation_mode = False
        
        # PLC Config
        self.plc_ip = "192.168.0.1"
        self.plc_rack = 0
        self.plc_slot = 1
        
        # OPC Config
        self.opc_host = "localhost" # เพิ่ม Hostเผื่อต่อ LAN
        self.opc_server_name = "KONE.OPC.DA.Server.4.0.0"
        self.opc_topic_prefix = "" # ถ้ามี prefix ร่วมกัน
        
        # Tags List (List of strings)
        self.opc_tag_list = [
            "Mektec.Factory3.SL1.SL1.ActualPosition",
            "Mektec.Factory3.SL1.SL1.LiftMode"
        ] # ค่าเริ่มต้น
        
        # --- Live Data ---
        self.opc_values = {}    # เก็บค่าล่าสุด { "TagName": Value }
        self.plc_data = {}      # เก็บค่า PLC
        
        # --- Status ---
        self.opc_connected = False
        self.plc_connected = False
        
        # --- Logs ---
        self.log_queue = []
        
        self._initialized = True

    def log(self, source, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] [{source}] {message}"
        print(entry)
        with self.data_lock:
            self.log_queue.append(entry)
            if len(self.log_queue) > 100:
                self.log_queue.pop(0)

    def update_opc_data(self, tag_name, value):
        with self.data_lock:
            self.opc_values[tag_name] = value

    def update_plc_data(self, key, value):
        with self.data_lock:
            self.plc_data[key] = value

    def get_logs(self):
        with self.data_lock:
            return list(self.log_queue)

state = AppState()