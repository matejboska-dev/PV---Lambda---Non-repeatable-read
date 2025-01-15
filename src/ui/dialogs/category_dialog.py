# ui/dialogs/category_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QCheckBox, QPushButton, QMessageBox,
                           QTextEdit)

class CategoryDialog(QDialog):
    def __init__(self, db, category=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.category = category
        self.init_ui()
        if category:
            self.load_category_data()

    def init_ui(self):
        self.setWindowTitle("Přidat kategorii" if not self.category else "Upravit kategorii")
        layout = QVBoxLayout(self)

        # Název
        layout.addWidget(QLabel("Název:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)

        # Popis
        layout.addWidget(QLabel("Popis:"))
        self.description_edit = QTextEdit()
        layout.addWidget(self.description_edit)

        # Aktivní
        self.active_check = QCheckBox("Aktivní")
        self.active_check.setChecked(True)
        layout.addWidget(self.active_check)

        # Tlačítka
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Uložit")
        save_btn.clicked.connect(self.save_category)
        cancel_btn = QPushButton("Zrušit")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def load_category_data(self):
        cursor = self.db.connection.cursor()
        cursor.execute("""
            SELECT Name, Description, IsActive 
            FROM Categories 
            WHERE CategoryID = ?
        """, (self.category,))
        data = cursor.fetchone()
        
        if data:
            self.name_edit.setText(data[0])
            self.description_edit.setText(data[1] if data[1] else "")
            self.active_check.setChecked(data[2])

    def save_category(self):
        try:
            name = self.name_edit.text()
            description = self.description_edit.toPlainText()
            is_active = self.active_check.isChecked()

            cursor = self.db.connection.cursor()
            
            if self.category:  # Úprava existující kategorie
                cursor.execute("""
                    UPDATE Categories 
                    SET Name = ?, Description = ?, IsActive = ?
                    WHERE CategoryID = ?
                """, (name, description, is_active, self.category))
            else:  # Nová kategorie
                cursor.execute("""
                    INSERT INTO Categories (Name, Description, IsActive)
                    VALUES (?, ?, ?)
                """, (name, description, is_active))
            
            self.db.connection.commit()
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Nelze uložit kategorii: {str(e)}")