import threading
import time
import queue
import pythoncom
import win32com.client
from core.logger import logger
from config import settings

class OPCClient(threading.Thread):
    def __init__(self, data_queue):
        super().__init__(daemon=True, name="OPC-Thread")
        self.data_queue = data_queue
        self.running = True
        self.connected = False

    def run(self):
        pythoncom.CoInitialize()
        while self.running:
            try:
                self._connect_and_listen()
            except Exception as e:
                logger.error(f"OPC error: {e}")
                self.connected = False
                time.sleep(settings.OPC_AUTO_RECONNECT_SEC)

    def _connect_and_listen(self):
        logger.info("Connecting OPC DA...")
        opc = win32com.client.Dispatch("OPC.Automation")
        servers = opc.GetOPCServers("localhost")
        opc.Connect(servers[0], "localhost")

        group = opc.OPCGroups.Add("ASYNC")
        group.IsSubscribed = True
        group.UpdateRate = settings.OPC_UPDATE_RATE_MS

        win32com.client.WithEvents(group, self._Events(self.data_queue))
        self.connected = True
        logger.info("OPC connected")

        while self.running:
            pythoncom.PumpWaitingMessages()
            time.sleep(0.05)

    class _Events:
        def __init__(self, q):
            self.q = q

        def OnDataChange(self, *_args):
            # ส่ง raw event เข้า queue
            self.q.put(("opc", _args))
