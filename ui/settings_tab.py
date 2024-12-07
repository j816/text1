# project_root/ui/settings_tab.py

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QSlider, QHBoxLayout, QMessageBox)
from PyQt6.QtCore import Qt

class SettingsTab(QWidget):
    def __init__(self, settings_manager, secure_storage, openai_interface):
        super().__init__()
        self.settings_manager = settings_manager
        self.secure_storage = secure_storage
        self.openai_interface = openai_interface

        layout = QVBoxLayout()

        # API Key
        self.api_key_label = QLabel("OpenAI API Key:")
        self.api_key_field = QLineEdit()
        # Do not populate with stored API key for security; leave blank
        self.api_key_save_button = QPushButton("Save API Key")

        layout.addWidget(self.api_key_label)
        layout.addWidget(self.api_key_field)
        layout.addWidget(self.api_key_save_button)

        # Refresh Models
        self.openai_refresh_button = QPushButton("Refresh Models")
        self.model_selector_dropdown = QComboBox()
        layout.addWidget(self.openai_refresh_button)
        layout.addWidget(QLabel("OpenAI Models:"))
        layout.addWidget(self.model_selector_dropdown)

        # Temperature Slider
        self.temp_label = QLabel("Temperature:")
        self.temperature_slider = QSlider(Qt.Orientation.Horizontal)
        self.temperature_slider.setRange(0, 100)  # map 0-100 to 0.0-1.0
        self.temperature_slider.setValue(int(self.settings_manager.get("temperature", 0.7)*100))
        self.temperature_value_label = QLabel(str(self.settings_manager.get("temperature", 0.7)))

        temp_layout = QHBoxLayout()
        temp_layout.addWidget(self.temp_label)
        temp_layout.addWidget(self.temperature_slider)
        temp_layout.addWidget(self.temperature_value_label)
        layout.addLayout(temp_layout)

        # Monitoring Interval
        self.monitoring_interval_label = QLabel("Monitoring Interval (seconds):")
        self.monitoring_interval_field = QLineEdit(str(self.settings_manager.get("monitoring_interval", 20)))
        layout.addWidget(self.monitoring_interval_label)
        layout.addWidget(self.monitoring_interval_field)

        # Save settings button
        self.save_settings_button = QPushButton("Save Settings")
        layout.addWidget(self.save_settings_button)

        self.setLayout(layout)

        self.api_key_save_button.clicked.connect(self.save_api_key)
        self.openai_refresh_button.clicked.connect(self.refresh_models)
        self.model_selector_dropdown.currentIndexChanged.connect(self.model_changed)
        self.temperature_slider.valueChanged.connect(self.temperature_changed)
        self.save_settings_button.clicked.connect(self.save_settings)

        # Load models into dropdown
        self.load_models()

    def save_api_key(self):
        api_key = self.api_key_field.text().strip()
        if api_key:
            self.secure_storage.store_api_key(api_key)
            QMessageBox.information(self, "Success", "API Key saved securely.")
            self.api_key_field.clear()
        else:
            QMessageBox.warning(self, "Error", "Please enter a valid API Key.")

    def refresh_models(self):
        # Refresh models from OpenAI
        api_key = self.secure_storage.retrieve_api_key()
        if not api_key:
            QMessageBox.warning(self, "Error", "No API Key found. Please save your API Key first.")
            return
        oi = self.openai_interface
        models = oi.refresh_models()
        self.settings_manager.set("models_list", models)
        self.load_models()

    def load_models(self):
        self.model_selector_dropdown.clear()
        models = self.settings_manager.get("models_list", [])
        if models:
            self.model_selector_dropdown.addItems(models)
        current_model = self.settings_manager.get("model", "gpt-4")
        if current_model in models:
            self.model_selector_dropdown.setCurrentText(current_model)

    def model_changed(self):
        selected_model = self.model_selector_dropdown.currentText()
        self.settings_manager.set("model", selected_model)

    def temperature_changed(self):
        val = self.temperature_slider.value() / 100.0
        self.temperature_value_label.setText(f"{val:.2f}")

    def save_settings(self):
        # Save temperature and monitoring interval
        temp_val = float(self.temperature_slider.value())/100.0
        self.settings_manager.set("temperature", temp_val)
        try:
            interval = int(self.monitoring_interval_field.text().strip())
        except ValueError:
            interval = 20
        self.settings_manager.set("monitoring_interval", interval)
        QMessageBox.information(self, "Success", "Settings saved.")
