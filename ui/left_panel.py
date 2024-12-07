# project_root/ui/left_panel.py

import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QTextEdit, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextOption
from config import COMBINE_FORMAT

class LeftPanel(QWidget):
    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager

        self.criteria_label = QLabel("TextInputCriteria")
        self.file_selector_button = QPushButton("Select Criteria Directory")
        self.file_dropdown = QComboBox()

        self.input_label = QLabel("InputWorkingText")
        self.input_text_field = QTextEdit()
        self.input_text_field.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        self.token_counter_display = QLabel("Token Count: 0")
        self.send_to_gpt_button = QPushButton("Send to GPT")

        layout = QVBoxLayout()
        layout.addWidget(self.criteria_label)
        layout.addWidget(self.file_selector_button)
        layout.addWidget(self.file_dropdown)

        layout.addWidget(self.input_label)
        layout.addWidget(self.input_text_field)
        layout.addWidget(self.token_counter_display)
        layout.addWidget(self.send_to_gpt_button)

        self.setLayout(layout)

        # Load persisted criteria file if available
        criteria_file = self.settings_manager.get("criteria_file", "")
        criteria_dir = os.path.dirname(criteria_file) if criteria_file else ""
        if criteria_dir and os.path.isdir(criteria_dir):
            self.populate_file_dropdown(criteria_dir, preselect=criteria_file)

        self.file_selector_button.clicked.connect(self.select_criteria_directory)
        self.file_dropdown.currentIndexChanged.connect(self.on_criteria_file_selected)
        self.input_text_field.textChanged.connect(self.update_token_count)
        self.send_to_gpt_button.clicked.connect(self.send_to_gpt)

        self.update_send_button_state()

    def select_criteria_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Criteria Directory")
        if directory:
            self.populate_file_dropdown(directory)

    def populate_file_dropdown(self, directory, preselect=""):
        self.file_dropdown.clear()
        allowed_extensions = [".txt", ".md", ".json"]
        files = [f for f in os.listdir(directory) if os.path.splitext(f)[1].lower() in allowed_extensions]
        for f in files:
            self.file_dropdown.addItem(os.path.join(directory, f))
        if preselect and preselect in [os.path.join(directory, f) for f in files]:
            self.file_dropdown.setCurrentText(preselect)

    def on_criteria_file_selected(self):
        selected_file = self.file_dropdown.currentText()
        self.settings_manager.set("criteria_file", selected_file)
        self.update_send_button_state()

    def update_token_count(self):
        text = self.input_text_field.toPlainText()
        # Simplified token counting (in reality, use a proper tokenizer)
        tokens = text.split()
        self.token_counter_display.setText(f"Token Count: {len(tokens)}")
        self.settings_manager.set("input_text", text)
        self.update_send_button_state()

    def update_send_button_state(self):
        # Enable the button only if both input text and criteria file are present
        input_text = self.input_text_field.toPlainText().strip()
        criteria_file = self.file_dropdown.currentText().strip()
        if input_text and criteria_file:
            self.send_to_gpt_button.setEnabled(True)
        else:
            self.send_to_gpt_button.setEnabled(False)

    def send_to_gpt(self):
        input_text = self.input_text_field.toPlainText().strip()
        criteria_file_path = self.file_dropdown.currentText().strip()
        if not input_text or not criteria_file_path:
            QMessageBox.warning(self, "Error", "Please provide both input text and criteria file.")
            return

        # Load criteria file content
        if os.path.exists(criteria_file_path):
            with open(criteria_file_path, "r", encoding="utf-8") as f:
                criteria_content = f.read()
        else:
            QMessageBox.warning(self, "Error", "Selected criteria file no longer exists.")
            return

        combined = COMBINE_FORMAT.format(input_text=input_text, criteria_content=criteria_content)
        # Store combined text in settings or pass to a processing function
        # For now, just store it:
        self.settings_manager.set("combined_input", combined)
        QMessageBox.information(self, "Success", "Combined text has been prepared and sent to GPT (simulation).")
