# project_root/main.py

import sys
import os
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from settings_manager import SettingsManager
from secure_storage import SecureStorage

def ensure_settings_file():
    resources_path = os.path.join(os.path.dirname(__file__), "resources")
    if not os.path.exists(resources_path):
        os.makedirs(resources_path)
    settings_path = os.path.join(resources_path, "settings.json")
    if not os.path.exists(settings_path):
        # Create default settings.json
        with open(settings_path, "w", encoding="utf-8") as f:
            f.write('{\n    "folders": {}\n}')
    return settings_path

if __name__ == "__main__":
    app = QApplication(sys.argv)

    settings_path = ensure_settings_file()
    settings_manager = SettingsManager(settings_path)
    secure_storage = SecureStorage()

    window = MainWindow(settings_manager, secure_storage)
    window.resize(1200, 800)
    window.show()

    sys.exit(app.exec())
