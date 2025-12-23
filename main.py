from GUI.app import App
from core.opc_worker import OPCWorker
from core.plc_worker import PLCWorker
import sys

if __name__ == "__main__":
    print("Starting Application...")

    # 1. Start Background Threads
    opc_thread = OPCWorker()
    plc_thread = PLCWorker()

    opc_thread.start()
    plc_thread.start()

    # 2. Start GUI (Main Thread)
    # GUI ต้องรันใน Main Thread เสมอ
    try:
        app = App()
        app.mainloop()
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        # 3. Cleanup Clean Exit
        opc_thread.stop()
        plc_thread.stop()
        sys.exit(0)