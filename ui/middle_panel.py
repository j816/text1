# project_root/ui/middle_panel.py

import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTextEdit, QLineEdit, QPushButton, QFileDialog, QMessageBox)
from PyQt6.QtGui import QTextOption

class MiddlePanel(QWidget):
    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager

        self.label = QLabel("InputTextProcess1")
        self.markdown_editor_response = QTextEdit()
        self.markdown_editor_response.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        self.delimiter_input_field = QLineEdit()
        self.filename_suffix_input = QLineEdit()
        self.filename_suffix_input.setText(self.settings_manager.get("suffix", "SPLIT"))
        self.save_and_split_button = QPushButton("Save & Split")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(QLabel("Response Markdown:"))
        layout.addWidget(self.markdown_editor_response)
        layout.addWidget(QLabel("Delimiter:"))
        layout.addWidget(self.delimiter_input_field)
        layout.addWidget(QLabel("Filename Suffix (optional):"))
        layout.addWidget(self.filename_suffix_input)
        layout.addWidget(self.save_and_split_button)

        self.setLayout(layout)

        self.save_and_split_button.clicked.connect(self.save_and_split)

    def save_and_split(self):
        delimiter = self.delimiter_input_field.text().strip()
        if not delimiter:
            QMessageBox.warning(self, "Error", "Please provide a valid delimiter.")
            return

        text = self.markdown_editor_response.toPlainText()
        parts = text.split(delimiter)
        if len(parts) < 2:
            QMessageBox.warning(self, "Error", "The text does not contain the specified delimiter.")
            return

        suffix = self.filename_suffix_input.text().strip()
        if not suffix:
            suffix = "SPLIT"

        # Ask user for output folder
        output_folder = QFileDialog.getExistingDirectory(self, "Select Split Files Destination")
        if not output_folder:
            return

        self.settings_manager.set_nested(output_folder, "folders", "split_folder")

        # Derive base filename from criteria file or input file if available
        base_filename = "split_output"
        criteria_file = self.settings_manager.get("criteria_file", "")
        if criteria_file:
            base_filename = os.path.splitext(os.path.basename(criteria_file))[0]

        # Save each part
        for i, part in enumerate(parts, start=1):
            out_filename = f"{base_filename}_split_{i}_{suffix}.md"
            out_path = os.path.join(output_folder, out_filename)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(part.strip())

        QMessageBox.information(self, "Success", f"Files saved successfully in {output_folder}.")
