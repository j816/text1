# project_root/ui/main_window.py

import os
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter
from PyQt6.QtCore import Qt

from .left_panel import LeftPanel
from .middle_panel import MiddlePanel
from .right_panel import RightPanel

class MainWindow(QMainWindow):
    def __init__(self, settings_manager, secure_storage):
        super().__init__()
        self.settings_manager = settings_manager
        self.secure_storage = secure_storage
        self.setWindowTitle("Text Processing Application")

        # Create main layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Create panels
        self.left_panel = LeftPanel(self.settings_manager)
        self.middle_panel = MiddlePanel(self.settings_manager)
        self.right_panel = RightPanel(self.settings_manager, self.secure_storage)

        # Use a QSplitter to separate the panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.left_panel)
        splitter.addWidget(self.middle_panel)
        splitter.addWidget(self.right_panel)

        main_layout.addWidget(splitter)
