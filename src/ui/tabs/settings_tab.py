# ui/tabs/settings_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLabel, QComboBox)

class SettingsTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        isolation_layout = QHBoxLayout()
        isolation_label = QLabel("Izolační úroveň:")
        self.isolation_combo = QComboBox()
        self.isolation_combo.addItems([
            "READ UNCOMMITTED",
            "READ COMMITTED",
            "REPEATABLE READ",
            "SERIALIZABLE"
        ])
        
        isolation_layout.addWidget(isolation_label)
        isolation_layout.addWidget(self.isolation_combo)
        isolation_layout.addStretch()
        
        layout.addLayout(isolation_layout)
        
        self.import_btn = QPushButton("Import dat")
        self.export_btn = QPushButton("Export dat")
        
        layout.addWidget(self.import_btn)
        layout.addWidget(self.export_btn)
        layout.addStretch()