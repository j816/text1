# project_root/ui/tagger_tab.py

import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QFileDialog, QMessageBox, QLineEdit)
from PyQt6.QtCore import QTimer
from config import COMBINE_FORMAT

class TaggerTab(QWidget):
    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager
        self.openai_interface = None
        self.monitoring_active = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_monitored_folder)

        layout = QVBoxLayout()

        # Tag Criteria Section
        self.tag_criteria_label = QLabel("Tag Criteria File:")
        self.tag_criteria_button = QPushButton("Select Criteria Directory")
        self.tag_criteria_dropdown = QComboBox()
        self.tag_criteria_dropdown.setMinimumWidth(300)
        self.tag_criteria_dropdown.setPlaceholderText("Select a criteria file...")

        # Monitored Folder Section
        self.monitored_folder_label = QLabel("Monitored Folder:")
        self.monitored_folder_button = QPushButton("Select Monitored Folder")
        self.monitored_folder_path_label = QLabel()
        self.monitored_folder_path_label.setStyleSheet("color: #666; padding: 5px;")
        self.monitored_folder_path_label.setWordWrap(True)

        # Tagged Output Folder Section
        self.saved_tagged_label = QLabel("Tagged Output Folder:")
        self.saved_tagged_button = QPushButton("Select Tagged Folder")
        self.saved_tagged_path_label = QLabel()
        self.saved_tagged_path_label.setStyleSheet("color: #666; padding: 5px;")
        self.saved_tagged_path_label.setWordWrap(True)

        # Tag Prefix Section
        self.tag_prefix_label = QLabel("Output File Prefix:")
        self.tag_prefix_input = QLineEdit()
        self.tag_prefix_input.setPlaceholderText("Optional prefix for tagged files...")
        self.tag_prefix_input.setText(self.settings_manager.get("tag_prefix", ""))
        self.tag_prefix_input.textChanged.connect(self.on_prefix_changed)

        # Add widgets to layout with proper spacing
        layout.addWidget(self.tag_criteria_label)
        layout.addWidget(self.tag_criteria_button)
        layout.addWidget(self.tag_criteria_dropdown)
        layout.addSpacing(15)

        layout.addWidget(self.monitored_folder_label)
        layout.addWidget(self.monitored_folder_button)
        layout.addWidget(self.monitored_folder_path_label)
        layout.addSpacing(15)

        layout.addWidget(self.saved_tagged_label)
        layout.addWidget(self.saved_tagged_button)
        layout.addWidget(self.saved_tagged_path_label)
        layout.addSpacing(15)

        layout.addWidget(self.tag_prefix_label)
        layout.addWidget(self.tag_prefix_input)
        layout.addSpacing(15)

        # Monitoring controls
        self.start_monitoring_button = QPushButton("Start Monitoring")
        self.stop_monitoring_button = QPushButton("Stop Monitoring")
        self.stop_monitoring_button.setEnabled(False)
        
        layout.addWidget(self.start_monitoring_button)
        layout.addWidget(self.stop_monitoring_button)
        layout.addStretch()  # Push everything up

        self.setLayout(layout)

        # Remove the monitored folder dropdown as it's not needed
        self.monitored_folder_dropdown = None

        # Load previously saved paths
        self._load_tag_criteria()
        self._load_monitored_folder()
        self._load_tagged_folder()

        # Connect signals
        self.tag_criteria_button.clicked.connect(self.select_criteria_directory)
        self.monitored_folder_button.clicked.connect(self.select_monitored_folder)
        self.saved_tagged_button.clicked.connect(self.select_tagged_folder)
        self.start_monitoring_button.clicked.connect(self.start_monitoring)
        self.stop_monitoring_button.clicked.connect(self.stop_monitoring)

        # Add dropdown selection change handler
        self.tag_criteria_dropdown.currentTextChanged.connect(self.on_criteria_file_changed)

    def set_openai_interface(self, openai_interface):
        """Set the OpenAI interface from RightPanel"""
        self.openai_interface = openai_interface

    def start_monitoring(self):
        if not self.openai_interface:
            QMessageBox.warning(self, "Error", "OpenAI interface not initialized.")
            return
            
        if not self.tag_criteria_dropdown.currentText():
            QMessageBox.warning(self, "Error", "Please select a tagging criteria file.")
            return
            
        monitored_folder = self.settings_manager.get("monitored_folder", "")
        if not monitored_folder or not os.path.isdir(monitored_folder):
            QMessageBox.warning(self, "Error", "Please select a valid monitored folder.")
            return
            
        self.monitoring_active = True
        interval = self.settings_manager.get("monitoring_interval", 20) * 1000  # Convert to milliseconds
        self.timer.start(interval)
        self.start_monitoring_button.setEnabled(False)
        self.stop_monitoring_button.setEnabled(True)

    def stop_monitoring(self):
        self.monitoring_active = False
        self.timer.stop()
        self.start_monitoring_button.setEnabled(True)
        self.stop_monitoring_button.setEnabled(False)

    def check_monitored_folder(self):
        if not self.monitoring_active:
            return
            
        monitored_folder = self.settings_manager.get("monitored_folder", "")
        tagged_folder = self.settings_manager.get("tagged_folder", "")
        
        if not all([monitored_folder, tagged_folder]):
            self.stop_monitoring()
            return
            
        # Get list of files and immediately filter out zero-byte files
        allowed_extensions = [".txt", ".md"]
        files_to_process = []
        
        for f in os.listdir(monitored_folder):
            if os.path.splitext(f)[1].lower() not in allowed_extensions:
                continue
            
            input_path = os.path.join(monitored_folder, f)
            
            # Check for zero-byte files immediately
            if os.path.getsize(input_path) == 0:
                try:
                    os.remove(input_path)
                    print(f"Deleted zero-byte file: {f}")
                except Exception as e:
                    print(f"Error deleting zero-byte file {f}: {str(e)}")
                continue
            
            files_to_process.append(f)
                
        prefix = self.settings_manager.get("tag_prefix", "")
        for filename in files_to_process:
            input_path = os.path.join(monitored_folder, filename)
            if prefix:
                output_filename = f"{prefix}_{filename}"
            else:
                output_filename = filename
            output_path = os.path.join(tagged_folder, output_filename)
            
            # Skip if output file already exists
            if os.path.exists(output_path):
                continue
                
            try:
                # Read input file
                with open(input_path, "r", encoding="utf-8") as f:
                    input_text = f.read()
                    
                # Read criteria file
                criteria_file = self.tag_criteria_dropdown.currentText()
                with open(criteria_file, "r", encoding="utf-8") as f:
                    criteria_content = f.read()
                    
                # Combine using the template
                combined = COMBINE_FORMAT.format(
                    input_text=input_text.strip(),
                    criteria_content=criteria_content.strip()
                )
                
                # Send to GPT
                response = self.openai_interface.send_text(combined)
                
                if "error" in response:
                    print(f"Error processing {filename}: {response['error']}")
                    continue
                    
                # Save the tagged output
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(response["content"])
                    
                # Delete the source file after successful processing
                try:
                    os.remove(input_path)
                    print(f"Successfully processed and deleted: {filename}")
                except Exception as e:
                    print(f"Error deleting file {filename}: {str(e)}")
                    
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

    def select_criteria_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Criteria Directory")
        if directory:
            self.populate_file_dropdown(self.tag_criteria_dropdown, directory)
            # The selection change will be handled by on_criteria_file_changed

    def select_monitored_folder(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Monitored Folder")
        if directory:
            self.settings_manager.set("monitored_folder", directory)
            self.monitored_folder_path_label.setText(f"Selected: {directory}")

    def select_tagged_folder(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Tagged Folder")
        if directory:
            self.settings_manager.set("tagged_folder", directory)
            self.saved_tagged_path_label.setText(f"Selected: {directory}")

    def populate_file_dropdown(self, dropdown, directory):
        dropdown.clear()
        allowed_extensions = [".txt", ".md", ".json"]
        files = [f for f in os.listdir(directory) if os.path.splitext(f)[1].lower() in allowed_extensions]
        for f in files:
            # Add the full path to the dropdown
            full_path = os.path.join(directory, f)
            dropdown.addItem(full_path)

    def _load_tag_criteria(self):
        criteria_file = self.settings_manager.get("tag_criteria_file", "")
        if criteria_file and os.path.exists(criteria_file):
            criteria_dir = os.path.dirname(criteria_file)
            self.populate_file_dropdown(self.tag_criteria_dropdown, criteria_dir)
            # Set the dropdown to the saved full path
            self.tag_criteria_dropdown.setCurrentText(criteria_file)

    def _load_monitored_folder(self):
        monitored_folder = self.settings_manager.get("monitored_folder", "")
        if monitored_folder and os.path.isdir(monitored_folder):
            self.monitored_folder_path_label.setText(f"Selected: {monitored_folder}")

    def _load_tagged_folder(self):
        tagged_folder = self.settings_manager.get("tagged_folder", "")
        if tagged_folder and os.path.isdir(tagged_folder):
            self.saved_tagged_path_label.setText(f"Selected: {tagged_folder}")

    def on_criteria_file_changed(self, file_path):
        """Handle criteria file selection changes"""
        if file_path and os.path.exists(file_path):
            full_path = os.path.abspath(file_path)
            self.settings_manager.set("tag_criteria_file", full_path)

    def on_prefix_changed(self, text):
        """Save the prefix when it changes"""
        self.settings_manager.set("tag_prefix", text)
