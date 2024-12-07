# project_root/ui/left_panel.py

import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QTextEdit, QFileDialog, QMessageBox, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QTextOption, QSyntaxHighlighter, QTextCharFormat, QColor
from config import COMBINE_FORMAT
import tiktoken
import re

class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._formats = {
            'header': self._create_format(QColor("#0000FF")),  # Blue for headers
            'emphasis': self._create_format(QColor("#FF00FF")), # Magenta for emphasis
            'list': self._create_format(QColor("#008000")),     # Green for lists
        }

    def _create_format(self, color):
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        return fmt

    def highlightBlock(self, text):
        # Basic markdown highlighting
        # Headers
        for match in re.finditer(r'^#{1,6}\s.*$', text):
            self.setFormat(match.start(), match.end() - match.start(), self._formats['header'])
        # Lists
        for match in re.finditer(r'^\s*[\*\-\+]\s.*$', text):
            self.setFormat(match.start(), match.end() - match.start(), self._formats['list'])
        # Emphasis
        for match in re.finditer(r'\*\*.*?\*\*|\*.*?\*|__.*?__|_.*?_', text):
            self.setFormat(match.start(), match.end() - match.start(), self._formats['emphasis'])

class LeftPanel(QWidget):
    gpt_response_received = pyqtSignal(str)
    
    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager
        self.openai_interface = None  # Will be set from MainWindow
        # Initialize tokenizer for GPT-4 (or get from settings)
        self.tokenizer = tiktoken.encoding_for_model("gpt-4")
        
        self.criteria_label = QLabel("TextInputCriteria")
        self.file_selector_button = QPushButton("Select Criteria Directory")
        self.file_dropdown = QComboBox()

        self.input_label = QLabel("InputWorkingText")
        self.input_text_field = QTextEdit()
        self.input_text_field.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        self.input_text_field.setAcceptRichText(False)  # Force plain text mode
        self.input_text_field.setPlaceholderText("Enter markdown text here...")
        
        # Add markdown highlighter
        self.markdown_highlighter = MarkdownHighlighter(self.input_text_field.document())
        
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
        criteria_file = self.settings_manager.get("text_input_criteria_file", "")
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
        self.settings_manager.set("text_input_criteria_file", selected_file)
        self.update_send_button_state()

    def update_token_count(self):
        text = self.input_text_field.toPlainText()
        # Use tiktoken for accurate token counting
        try:
            tokens = self.tokenizer.encode(text)
            token_count = len(tokens)
            self.token_counter_display.setText(f"Token Count: {token_count}")
        except Exception as e:
            # Fallback to simple counting if tokenizer fails
            tokens = text.split()
            self.token_counter_display.setText(f"Token Count (estimate): {len(tokens)}")
            print(f"Tokenizer error: {str(e)}")
        
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

    def set_openai_interface(self, openai_interface):
        self.openai_interface = openai_interface

    def send_to_gpt(self):
        if not self.openai_interface:
            QMessageBox.warning(self, "Error", "OpenAI interface not initialized.")
            return

        input_text = self.input_text_field.toPlainText().strip()
        criteria_file_path = self.file_dropdown.currentText().strip()
        if not input_text or not criteria_file_path:
            QMessageBox.warning(self, "Error", "Please provide both input text and criteria file.")
            return

        try:
            # Load criteria file content
            with open(criteria_file_path, "r", encoding="utf-8") as f:
                criteria_content = f.read()
                
            # Format the prompt using the template
            combined = COMBINE_FORMAT.format(
                input_text=input_text.strip(),
                criteria_content=criteria_content.strip()
            )
            
            # Show processing indicator
            self.send_to_gpt_button.setEnabled(False)
            self.send_to_gpt_button.setText("Processing...")
            QApplication.processEvents()
            
            try:
                # Send to GPT and get response
                response = self.openai_interface.send_text(combined)
                
                if "error" in response:
                    QMessageBox.warning(self, "Error", f"API Error: {response['error']}")
                    return
                    
                # Store the response and emit signal
                self.settings_manager.set("last_response", response["content"])
                self.gpt_response_received.emit(response["content"])
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to send to GPT: {str(e)}")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error reading criteria file: {str(e)}")
        finally:
            # Reset button state
            self.send_to_gpt_button.setEnabled(True)
            self.send_to_gpt_button.setText("Send to GPT")

    def update_tokenizer(self, model_name="gpt-4"):
        try:
            self.tokenizer = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # Fallback to cl100k_base encoding if model not found
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
