# project_root/ui/tagger_tab.py

import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QFileDialog, QMessageBox)

class TaggerTab(QWidget):
    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager

        layout = QVBoxLayout()

        # Tag Criteria
        self.tag_criteria_label = QLabel("Tag Criteria")
        self.tag_criteria_button = QPushButton("Select Criteria Directory")
        self.tag_criteria_dropdown = QComboBox()

        # Monitored Folder
        self.monitored_folder_label = QLabel("Monitored Folder")
        self.monitored_folder_button = QPushButton("Select Monitored Folder")
        self.monitored_folder_dropdown = QComboBox()

        # Saved Tagged
        self.saved_tagged_label = QLabel("Saved Tagged")
        self.saved_tagged_button = QPushButton("Select Tagged Folder")

        layout.addWidget(self.tag_criteria_label)
        layout.addWidget(self.tag_criteria_button)
        layout.addWidget(self.tag_criteria_dropdown)

        layout.addWidget(self.monitored_folder_label)
        layout.addWidget(self.monitored_folder_button)
        layout.addWidget(self.monitored_folder_dropdown)

        layout.addWidget(self.saved_tagged_label)
        layout.addWidget(self.saved_tagged_button)

        self.setLayout(layout)

        # Load previously saved paths
        self._load_tag_criteria()
        self._load_monitored_folder()

        self.tag_criteria_button.clicked.connect(self.select_criteria_directory)
        self.monitored_folder_button.clicked.connect(self.select_monitored_folder)
        self.saved_tagged_button.clicked.connect(self.select_tagged_folder)

    def select_criteria_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Criteria Directory")
        if directory:
            self.populate_file_dropdown(self.tag_criteria_dropdown, directory)
            # Save first file if any
            if self.tag_criteria_dropdown.count() > 0:
                self.settings_manager.set("criteria_file", self.tag_criteria_dropdown.currentText())

    def select_monitored_folder(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Monitored Folder")
        if directory:
            self.populate_file_dropdown(self.monitored_folder_dropdown, directory)
            self.settings_manager.set("monitored_folder", directory)

    def select_tagged_folder(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Tagged Folder")
        if directory:
            self.settings_manager.set("tagged_folder", directory)

    def populate_file_dropdown(self, dropdown, directory):
        dropdown.clear()
        allowed_extensions = [".txt", ".md", ".json"]
        files = [f for f in os.listdir(directory) if os.path.splitext(f)[1].lower() in allowed_extensions]
        for f in files:
            dropdown.addItem(os.path.join(directory, f))

    def _load_tag_criteria(self):
        criteria_file = self.settings_manager.get("criteria_file", "")
        if criteria_file and os.path.exists(criteria_file):
            criteria_dir = os.path.dirname(criteria_file)
            self.populate_file_dropdown(self.tag_criteria_dropdown, criteria_dir)
            self.tag_criteria_dropdown.setCurrentText(criteria_file)

    def _load_monitored_folder(self):
        monitored_folder = self.settings_manager.get("monitored_folder", "")
        if monitored_folder and os.path.isdir(monitored_folder):
            self.populate_file_dropdown(self.monitored_folder_dropdown, monitored_folder)
