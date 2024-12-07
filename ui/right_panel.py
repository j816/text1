# project_root/ui/right_panel.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from .tagger_tab import TaggerTab
from .settings_tab import SettingsTab
from openai_interface import OpenAIInterface

class RightPanel(QWidget):
    def __init__(self, settings_manager, secure_storage):
        super().__init__()
        self.settings_manager = settings_manager
        self.secure_storage = secure_storage
        api_key = self.secure_storage.retrieve_api_key()
        model = self.settings_manager.get("model", "gpt-4")
        temperature = self.settings_manager.get("temperature", 0.7)
        self.openai_interface = OpenAIInterface(api_key, model, temperature)

        layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tagger_tab = TaggerTab(self.settings_manager)
        self.settings_tab = SettingsTab(self.settings_manager, self.secure_storage, self.openai_interface)

        self.tabs.addTab(self.tagger_tab, "Tagger")
        self.tabs.addTab(self.settings_tab, "Settings")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

        # Pass OpenAI interface to TaggerTab
        self.tagger_tab.set_openai_interface(self.openai_interface)
