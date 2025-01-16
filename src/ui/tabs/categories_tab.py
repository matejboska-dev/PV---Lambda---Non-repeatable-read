# ui/tabs/categories_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QMessageBox, QDialog)
from PyQt6.QtCore import Qt
from ui.dialogs.category_dialog import CategoryDialog

class CategoriesTab(QWidget):
    def __init__(self, db, main_window):  # Přidáme main_window parametr
        super().__init__()
        self.db = db
        self.main_window = main_window  # Uložíme referenci na hlavní okno
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Horní panel s tlačítky
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Přidat kategorii")
        self.edit_btn = QPushButton("Upravit kategorii")
        self.delete_btn = QPushButton("Smazat kategorii")
        
        self.add_btn.clicked.connect(self.add_category)
        self.edit_btn.clicked.connect(self.edit_category)
        self.delete_btn.clicked.connect(self.delete_category)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Tabulka kategorií
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.table)

    def add_category(self):
        dialog = CategoryDialog(self.db, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            self.main_window.status_bar.showMessage("Kategorie byla přidána")

    def edit_category(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Varování", "Vyberte kategorii k úpravě")
            return
            
        category_id = int(self.table.item(selected[0].row(), 0).text())
        dialog = CategoryDialog(self.db, category_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            self.main_window.status_bar.showMessage("Kategorie byla upravena")

    def delete_category(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Varování", "Vyberte kategorii ke smazání")
            return
            
        category_id = int(self.table.item(selected[0].row(), 0).text())
        
        # Kontrola, zda kategorie neobsahuje produkty
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM Products WHERE CategoryID = ?", (category_id,))
        if cursor.fetchone()[0] > 0:
            QMessageBox.warning(self, "Varování", 
                              "Nelze smazat kategorii, která obsahuje produkty")
            return
        
        reply = QMessageBox.question(self, "Potvrdit smazání",
                                   "Opravdu chcete smazat tuto kategorii?",
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
                                   
        if reply == QMessageBox.StandardButton.Yes:
            try:
                cursor = self.db.connection.cursor()
                cursor.execute("DELETE FROM Categories WHERE CategoryID = ?", 
                             (category_id,))
                self.db.connection.commit()
                self.load_data()
                self.main_window.status_bar.showMessage("Kategorie byla smazána")
            except Exception as e:
                QMessageBox.critical(self, "Chyba", 
                                   f"Nelze smazat kategorii: {str(e)}")

    def load_data(self):
        try:
            headers = ['ID', 'Název', 'Popis', 'Aktivní']
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)

            cursor = self.db.connection.cursor()
            cursor.execute("SELECT CategoryID, Name, Description, IsActive FROM Categories")
            
            data = cursor.fetchall()
            self.table.setRowCount(len(data))
            
            for row, item in enumerate(data):
                for col, value in enumerate(item):
                    if col == 3:  # IsActive
                        value = "Ano" if value else "Ne"
                    table_item = QTableWidgetItem(str(value))
                    table_item.setFlags(table_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(row, col, table_item)

            self.table.resizeColumnsToContents()
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Nepodařilo se načíst kategorie: {str(e)}")
            return False