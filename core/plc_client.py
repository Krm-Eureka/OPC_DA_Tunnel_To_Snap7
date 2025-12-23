import threading
import time
from core.logger import logger
from config import settings

class PLCClient(threading.Thread):
    def __init__(self, data_queue):
        super().__init__(daemon=True, name="PLC-Thread")
        self.queue = data_queue
        self.running = True

    def run(self):
        while self.running:
            try:
                self._connect()
                self._poll()
            except Exception as e:
                logger.error(f"PLC error: {e}")
                time.sleep(settings.PLC_AUTO_RECONNECT_SEC)

    def _connect(self):
        logger.info("PLC connected (mock)")

    def _poll(self):
        while self.running:
            self.queue.put(("plc", {"DB1.DBW0": 123}))
            time.sleep(settings.PLC_POLL_INTERVAL_SEC)
