# ui/dialogs/demo_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTextEdit, 
                           QPushButton, QLabel)
from PyQt6.QtCore import Qt

class DemoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Demonstrace Non-repeatable reads")
        self.setMinimumSize(500, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Text o aktuální izolační úrovni
        self.isolation_label = QLabel()
        layout.addWidget(self.isolation_label)
        
        # Log okno
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)
        
        # Tlačítko pro zavření
        close_btn = QPushButton("Zavřít")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def add_log(self, message):
        self.log.append(message)