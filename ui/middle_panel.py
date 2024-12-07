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
        
        # Initialize delimiter with saved value
        self.delimiter_input_field = QLineEdit()
        self.delimiter_input_field.setText(self.settings_manager.get("delimiter", ","))
        # Save delimiter whenever it changes
        self.delimiter_input_field.textChanged.connect(self.save_delimiter)
        
        self.filename_suffix_input = QLineEdit()
        self.filename_suffix_input.setText(self.settings_manager.get("suffix", "SPLIT"))
        
        # Add folder selection button and label
        self.folder_selection_button = QPushButton("Select Output Folder")
        self.selected_folder_label = QLabel()
        self.update_folder_label()
        
        self.save_and_split_button = QPushButton("Save & Split")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(QLabel("Response Markdown:"))
        layout.addWidget(self.markdown_editor_response)
        layout.addWidget(QLabel("Delimiter:"))
        layout.addWidget(self.delimiter_input_field)
        layout.addWidget(QLabel("Filename Suffix (optional):"))
        layout.addWidget(self.filename_suffix_input)
        layout.addWidget(QLabel("Output Folder:"))
        layout.addWidget(self.folder_selection_button)
        layout.addWidget(self.selected_folder_label)
        layout.addWidget(self.save_and_split_button)

        self.setLayout(layout)

        # Connect the new button
        self.folder_selection_button.clicked.connect(self.select_output_folder)
        self.save_and_split_button.clicked.connect(self.save_and_split)

    def update_folder_label(self):
        """Update the label showing the currently selected split folder"""
        folder = self.settings_manager.get_nested("folders", "split_folder", default="")
        if folder:
            self.selected_folder_label.setText(folder)
        else:
            self.selected_folder_label.setText("No folder selected")

    def select_output_folder(self):
        """Handle output folder selection"""
        previous_folder = self.settings_manager.get_nested("folders", "split_folder", default="")
        output_folder = QFileDialog.getExistingDirectory(
            self, 
            "Select Split Files Destination",
            previous_folder
        )
        if output_folder:
            self.settings_manager.set_nested(output_folder, "folders", "split_folder")
            self.update_folder_label()

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

        # Use the selected folder directly instead of asking again
        output_folder = self.settings_manager.get_nested("folders", "split_folder", default="")
        if not output_folder:
            QMessageBox.warning(self, "Error", "Please select an output folder first.")
            return

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

    def save_delimiter(self):
        """Save the delimiter value when it changes"""
        delimiter = self.delimiter_input_field.text().strip()
        self.settings_manager.set("delimiter", delimiter)
