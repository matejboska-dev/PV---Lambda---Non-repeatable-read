# ui/tabs/products_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QMessageBox, QDialog, QComboBox, QLabel)
from PyQt6.QtCore import Qt
from ui.dialogs.product_dialog import ProductDialog
from ui.dialogs.demo_dialog import DemoDialog  

class ProductsTab(QWidget):
    def __init__(self, db, main_window):
        super().__init__()
        self.db = db
        self.main_window = main_window
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
        
        # Panel pro demonstraci Non-repeatable reads
        demo_layout = QHBoxLayout()
        
        # Výběr izolační úrovně
        isolation_label = QLabel("Izolační úroveň:")
        self.isolation_combo = QComboBox()
        self.isolation_combo.addItems([
            "READ UNCOMMITTED",
            "READ COMMITTED",
            "REPEATABLE READ",
            "SERIALIZABLE"
        ])
        self.isolation_combo.setCurrentText("READ COMMITTED")  # Výchozí úroveň
        self.isolation_combo.currentTextChanged.connect(self.change_isolation_level)
        
        demo_btn = QPushButton("Demonstrace Non-repeatable reads")
        demo_btn.clicked.connect(self.demonstrate_non_repeatable_reads)
        
        demo_layout.addWidget(isolation_label)
        demo_layout.addWidget(self.isolation_combo)
        demo_layout.addWidget(demo_btn)
        demo_layout.addStretch()
        
        layout.addLayout(demo_layout)
        
        # Tabulka produktů
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.table)

    def change_isolation_level(self, level):
        try:
            cursor = self.db.connection.cursor()
            cursor.execute(f"SET TRANSACTION ISOLATION LEVEL {level}")
            self.main_window.status_bar.showMessage(f"Izolační úroveň nastavena na: {level}")
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Nelze změnit izolační úroveň: {str(e)}")

    def demonstrate_non_repeatable_reads(self):
        # Zobrazíme instrukce uživateli
        QMessageBox.information(self, "Instrukce pro demonstraci", 
            """Pro demonstraci Non-repeatable reads:
            1. Otevřete si druhou instanci této aplikace v novém okně
            2. V této instanci klikněte OK - spustí se první čtení
            3. V druhé instanci změňte množství produktu
            4. V této instanci klikněte OK pro druhé čtení
            """)

        # První čtení
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Varování", "Vyberte produkt pro demonstraci")
            return
            
        row = selected[0].row()
        product_id = int(self.table.item(row, 0).text())
        
        cursor = self.db.connection.cursor()
        
        # První čtení
        cursor.execute("SELECT Name, StockQuantity FROM Products WHERE ProductID = ?", 
                    (product_id,))
        first_read = cursor.fetchone()
        
        QMessageBox.information(self, "První čtení", 
            f"""Stav produktu:
            Název: {first_read[0]}
            Množství: {first_read[1]}
            
            Nyní v druhé instanci aplikace změňte množství tohoto produktu
            a pak klikněte OK pro druhé čtení.""")
        
        # Druhé čtení
        cursor.execute("SELECT Name, StockQuantity FROM Products WHERE ProductID = ?", 
                    (product_id,))
        second_read = cursor.fetchone()
        
        QMessageBox.information(self, "Výsledek", 
            f"""První čtení:
            Množství: {first_read[1]}
            
            Druhé čtení:
            Množství: {second_read[1]}
            
            {'-' * 30}
            Izolační úroveň: {self.main_window.settings_tab.get_current_isolation_level()}
            {'Došlo k Non-repeatable read!' if first_read[1] != second_read[1] else 'Data zůstala konzistentní'}""")
        
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