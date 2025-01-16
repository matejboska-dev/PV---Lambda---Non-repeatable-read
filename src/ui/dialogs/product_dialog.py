# ui/dialogs/product_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QComboBox, QPushButton, QMessageBox,
                           QSpinBox, QDoubleSpinBox)

class ProductDialog(QDialog):
    def __init__(self, db, product=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.product = product
        self.init_ui()
        if product:
            self.load_product_data()

    def init_ui(self):
        self.setWindowTitle("Přidat produkt" if not self.product else "Upravit produkt")
        layout = QVBoxLayout(self)

        # Název
        layout.addWidget(QLabel("Název:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)

        # Kategorie
        layout.addWidget(QLabel("Kategorie:"))
        self.category_combo = QComboBox()
        self.load_categories()
        layout.addWidget(self.category_combo)

        # Cena
        layout.addWidget(QLabel("Cena:"))
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 1000000)
        self.price_spin.setDecimals(2)
        self.price_spin.setSuffix(" Kč")
        layout.addWidget(self.price_spin)

        # Množství
        layout.addWidget(QLabel("Množství:"))
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(0, 10000)
        layout.addWidget(self.quantity_spin)

        # Status
        layout.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(['available', 'discontinued', 'out_of_stock'])
        layout.addWidget(self.status_combo)

        # Tlačítka
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Uložit")
        save_btn.clicked.connect(self.save_product)
        cancel_btn = QPushButton("Zrušit")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def load_categories(self):
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT CategoryID, Name FROM Categories WHERE IsActive = 1")
            categories = cursor.fetchall()
            self.category_combo.clear()
            self.categories = {name: id for id, name in categories}
            self.category_combo.addItems(self.categories.keys())
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Nelze načíst kategorie: {str(e)}")

    def load_product_data(self):
        cursor = self.db.connection.cursor()
        cursor.execute("""
            SELECT p.Name, c.Name, p.Price, p.StockQuantity, p.Status
            FROM Products p
            JOIN Categories c ON p.CategoryID = c.CategoryID
            WHERE p.ProductID = ?
        """, (self.product,))
        data = cursor.fetchone()
        
        if data:
            self.name_edit.setText(data[0])
            self.category_combo.setCurrentText(data[1])
            self.price_spin.setValue(data[2])
            self.quantity_spin.setValue(data[3])
            self.status_combo.setCurrentText(data[4])

    def save_product(self):
        """Uloží nebo upraví produkt s použitím transakce"""
        try:
            # Získání hodnot před transakcí
            name = self.name_edit.text()
            category_id = self.categories[self.category_combo.currentText()]
            price = self.price_spin.value()
            quantity = self.quantity_spin.value()
            status = self.status_combo.currentText()

            cursor = self.db.connection.cursor()
            
            # Začátek transakce
            cursor.execute("BEGIN TRANSACTION")
            
            if self.product:  # Úprava existujícího produktu
                cursor.execute("""
                    UPDATE Products 
                    SET Name = ?, CategoryID = ?, Price = ?, 
                        StockQuantity = ?, Status = ?, LastUpdated = GETDATE()
                    WHERE ProductID = ?
                """, (name, category_id, price, quantity, status, self.product))
            else:  # Nový produkt
                cursor.execute("""
                    INSERT INTO Products (Name, CategoryID, Price, StockQuantity, Status)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, category_id, price, quantity, status))
            
            # Potvrzení transakce
            self.db.connection.commit()
            self.accept()
            
        except Exception as e:
            # Rollback v případě chyby
            self.db.connection.rollback()
            QMessageBox.critical(self, "Chyba", f"Nelze uložit produkt: {str(e)}")