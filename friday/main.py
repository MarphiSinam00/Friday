import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

def main():
    try:
        print("[Friday] Step 1: Initializing database...")
        from memory.database import init_db
        init_db()

        print("[Friday] Step 2: Starting connectivity monitor...")
        from core.connectivity import start_monitor
        start_monitor()

        print("[Friday] Step 3: Checking Ollama model...")
        from core.offline_llm import pull_model_if_needed
        pull_model_if_needed()

        print("[Friday] Step 4: Starting QApplication...")
        app = QApplication(sys.argv)
        app.setApplicationName("Friday")
        app.setFont(QFont("Segoe UI", 10))

        print("[Friday] Step 5: Creating main window...")
        from ui.main_window import MainWindow
        window = MainWindow()

        print("[Friday] Step 6: Showing window...")
        window.show()

        print("[Friday] Step 7: Running app loop...")
        sys.exit(app.exec())

    except Exception as e:
        import traceback
        print(f"[Friday] CRASH at: {e}")
        traceback.print_exc()
        input("Press Enter to close...")

if __name__ == "__main__":
    main()
