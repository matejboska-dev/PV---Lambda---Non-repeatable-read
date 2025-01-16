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
        self.refresh_btn = QPushButton("Refresh")
        
        self.add_btn.clicked.connect(self.add_product)
        self.edit_btn.clicked.connect(self.edit_product)
        self.delete_btn.clicked.connect(self.delete_product)
        self.refresh_btn.clicked.connect(self.refresh_data)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.refresh_btn)
        
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
        self.isolation_combo.setCurrentText("READ COMMITTED")
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
            self.main_window.status_bar.showMessage("Produkt byl přidán")

    def edit_product(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Varování", "Vyberte produkt k úpravě")
            return
            
        product_id = int(self.table.item(selected[0].row(), 0).text())
        dialog = ProductDialog(self.db, product_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            self.main_window.status_bar.showMessage("Produkt byl upraven")

    def delete_product(self):
        """Smaže produkt s použitím transakce"""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Varování", "Vyberte produkt ke smazání")
            return
            
        product_id = int(self.table.item(selected[0].row(), 0).text())
        
        try:
            cursor = self.db.connection.cursor()
            
            # Kontrola, zda produkt není v žádné objednávce
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
                # Začátek transakce
                cursor.execute("BEGIN TRANSACTION")
                try:
                    # Smazání produktu
                    cursor.execute("DELETE FROM Products WHERE ProductID = ?", (product_id,))
                    
                    # Potvrzení transakce
                    self.db.connection.commit()
                    self.load_data()
                    self.main_window.status_bar.showMessage("Produkt byl smazán")
                    
                except Exception as e:
                    # Rollback v případě chyby
                    self.db.connection.rollback()
                    raise e
                    
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Nelze smazat produkt: {str(e)}")

    def refresh_data(self):
        """Obnoví data v tabulce produktů"""
        if self.load_data():
            self.main_window.status_bar.showMessage("Data byla obnovena")

    def change_isolation_level(self, level):
        try:
            cursor = self.db.connection.cursor()
            cursor.execute(f"SET TRANSACTION ISOLATION LEVEL {level}")
            self.main_window.status_bar.showMessage(f"Izolační úroveň nastavena na: {level}")
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Nelze změnit izolační úroveň: {str(e)}")

    def demonstrate_non_repeatable_reads(self):
        """Demonstrace problému Non-repeatable reads s použitím transakce"""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Varování", "Vyberte produkt pro demonstraci")
            return
                
        row = selected[0].row()
        product_id = int(self.table.item(row, 0).text())
            
        try:
            cursor = self.db.connection.cursor()
            
            # Začátek transakce
            cursor.execute("BEGIN TRANSACTION")
            
            try:
                # První čtení v rámci transakce
                cursor.execute("SELECT Name, StockQuantity FROM Products WHERE ProductID = ?", 
                            (product_id,))
                first_read = cursor.fetchone()
                
                QMessageBox.information(
                    self,
                    "První čtení",
                    f"""Stav produktu:
                    Název: {first_read[0]}
                    Množství: {first_read[1]}
                    
                    Nyní v druhé instanci aplikace změňte množství tohoto produktu
                    a pak klikněte OK pro druhé čtení.
                    
                    Izolační úroveň: {self.isolation_combo.currentText()}""")
                
                # Druhé čtení ve stejné transakci
                cursor.execute("SELECT Name, StockQuantity FROM Products WHERE ProductID = ?", 
                            (product_id,))
                second_read = cursor.fetchone()
                
                # Ukončení transakce
                self.db.connection.commit()
                
                # Zobrazení výsledků
                message = f"""Výsledek demonstrace:

    První čtení:
    Název: {first_read[0]}
    Množství: {first_read[1]}

    Druhé čtení:
    Název: {second_read[0]}
    Množství: {second_read[1]}

    {'-' * 30}
    Izolační úroveň: {self.isolation_combo.currentText()}

    {'❌ Došlo k Non-repeatable read!' if first_read[1] != second_read[1] 
    else '✅ Data zůstala konzistentní'}

    Vysvětlení:
    {self._get_isolation_explanation(first_read[1] != second_read[1])}"""
                
                QMessageBox.information(self, "Výsledek demonstrace", message)
                
            except Exception as e:
                # Rollback v případě chyby
                self.db.connection.rollback()
                raise e
                
            finally:
                # Obnovíme data v tabulce
                self.load_data()
                    
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Chyba při demonstraci: {str(e)}")

    def _get_isolation_explanation(self, changed):
        """Vrátí vysvětlení podle izolační úrovně a výsledku"""
        level = self.isolation_combo.currentText()
        if level in ["READ UNCOMMITTED", "READ COMMITTED"]:
            if changed:
                return """Při této izolační úrovni není zajištěno, že opakované čtení 
                stejných dat vrátí stejné výsledky. To může vést k nekonzistentním 
                výsledkům v rámci jedné transakce."""
            else:
                return """I když data zůstala stejná, při této izolační úrovni 
                není garantováno, že opakované čtení vrátí stejné výsledky."""
        else:  # REPEATABLE READ nebo SERIALIZABLE
            if changed:
                return """Při této izolační úrovni by nemělo dojít ke změně dat 
                mezi čteními. Pokud vidíte rozdíl, může to být způsobeno 
                nestandardním chováním."""
            else:
                return """Tato izolační úroveň garantuje, že opakované čtení 
                stejných dat vrátí stejné výsledky, což se potvrdilo."""