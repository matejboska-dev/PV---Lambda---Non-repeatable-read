# ui/tabs/products_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QMessageBox, QDialog)
from PyQt6.QtCore import Qt
from ui.dialogs.product_dialog import ProductDialog

class ProductsTab(QWidget):
    def __init__(self, db, main_window):  # Přidáme parametr main_window
        super().__init__()
        self.db = db
        self.main_window = main_window  # Uložíme referenci na hlavní okno
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Horní panel s tlačítky
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Přidat produkt")
        self.edit_btn = QPushButton("Upravit produkt")
        self.delete_btn = QPushButton("Smazat produkt")
        
        self.add_btn.clicked.connect(self.add_product)
        self.edit_btn.clicked.connect(self.edit_product)
        self.delete_btn.clicked.connect(self.delete_product)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Tabulka produktů
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.table)

    def load_data(self):
        try:
            headers = ['ID', 'Kategorie', 'Název', 'Cena', 'Množství', 'Status']
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)

            cursor = self.db.connection.cursor()
            cursor.execute("""
                SELECT p.ProductID, c.Name as CategoryName, p.Name, 
                       p.Price, p.StockQuantity, p.Status
                FROM Products p
                JOIN Categories c ON p.CategoryID = c.CategoryID
            """)
            
            data = cursor.fetchall()
            self.table.setRowCount(len(data))
            
            for row, item in enumerate(data):
                for col, value in enumerate(item):
                    if col == 3:  # cena
                        value = f"{value:.2f} Kč"
                    table_item = QTableWidgetItem(str(value))
                    table_item.setFlags(table_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(row, col, table_item)

            self.table.resizeColumnsToContents()
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Nepodařilo se načíst produkty: {str(e)}")
            return False

    def add_product(self):
        dialog = ProductDialog(self.db, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            self.main_window.status_bar.showMessage("Produkt byl přidán")  # Použijeme main_window místo parent()

    def edit_product(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Varování", "Vyberte produkt k úpravě")
            return
            
        product_id = int(self.table.item(selected[0].row(), 0).text())
        dialog = ProductDialog(self.db, product_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            self.main_window.status_bar.showMessage("Produkt byl upraven")  # Použijeme main_window místo parent()

    def delete_product(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Varování", "Vyberte produkt ke smazání")
            return
            
        product_id = int(self.table.item(selected[0].row(), 0).text())
        
        # Kontrola, zda produkt není v žádné objednávce
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM OrderItems WHERE ProductID = ?", (product_id,))
        if cursor.fetchone()[0] > 0:
            QMessageBox.warning(self, "Varování", 
                              "Nelze smazat produkt, který je součástí objednávek")
            return
        
        reply = QMessageBox.question(self, "Potvrdit smazání",
                                   "Opravdu chcete smazat tento produkt?",
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
                                   
        if reply == QMessageBox.StandardButton.Yes:
            try:
                cursor = self.db.connection.cursor()
                cursor.execute("DELETE FROM Products WHERE ProductID = ?", (product_id,))
                self.db.connection.commit()
                self.load_data()
                self.main_window.status_bar.showMessage("Produkt byl smazán")  # Použijeme main_window místo parent()
            except Exception as e:
                QMessageBox.critical(self, "Chyba", f"Nelze smazat produkt: {str(e)}")