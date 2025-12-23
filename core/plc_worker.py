import threading
import time
import snap7
from snap7.util import get_dint
from core.state import state
import random

class PLCWorker(threading.Thread):
    def __init__(self):
        super().__init__(name="PLC-Worker", daemon=True)
        self.running = True
        self.client = snap7.client.Client()

    def run(self):
        state.log("PLC", "Thread Started")
        
        while self.running:
            if state.simulation_mode:
                self._run_simulation()
            else:
                self._run_real_plc()
            
            time.sleep(1) 
            
        if self.client.get_connected():
            self.client.disconnect()

    def _run_simulation(self):
        state.plc_connected = True
        # จำลองการอ่านค่า DB1.DBD0
        state.update_plc_data(0, random.randint(1000, 2000))

    def _run_real_plc(self):
        try:
            if not self.client.get_connected():
                state.log("PLC", f"Connecting to {state.plc_ip}...")
                self.client.connect(state.plc_ip, state.plc_rack, state.plc_slot)
                state.plc_connected = True
                state.log("PLC", "Connected")

            # Example: Read DB1, Start 0, Size 4 bytes (DInt)
            data = self.client.db_read(1, 0, 4)
            value = get_dint(data, 0)
            state.update_plc_data(0, value)

        except Exception as e:
            state.plc_connected = False
            state.log("PLC", f"Connection/Read Error: {e}")
            time.sleep(5)

    def stop(self):
        self.running = False