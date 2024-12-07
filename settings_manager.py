# project_root/settings_manager.py
import json
import os

class SettingsManager:
    def __init__(self, settings_path: str):
        self.settings_path = settings_path
        self.settings_data = {
            "folders": {
                "split_folder": "",
                "processed_folder": ""
            },
            "criteria_file": "",
            "input_text": "",
            "delimiter": ",",
            "suffix": "SPLIT",
            "monitored_folder": "",
            "tagged_folder": "",
            "model": "gpt-4",
            "temperature": 0.7,
            "monitoring_interval": 20
        }
        self._load_settings()

    def _load_settings(self):
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):  # Verify we got valid data
                        self.settings_data.update(data)
            except json.JSONDecodeError:
                # If file is corrupted, reset to defaults and save
                with open(self.settings_path, "w", encoding="utf-8") as f:
                    json.dump(self.settings_data, f, indent=4)

    def save_settings(self):
        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(self.settings_data, f, indent=4)

    def get(self, key, default=None):
        return self.settings_data.get(key, default)

    def set(self, key, value):
        self.settings_data[key] = value
        self.save_settings()

    def get_nested(self, *keys, default=None):
        data = self.settings_data
        for k in keys:
            data = data.get(k, {})
        return data if data else default

    def set_nested(self, value, *keys):
        data = self.settings_data
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        data[keys[-1]] = value
        self.save_settings()
