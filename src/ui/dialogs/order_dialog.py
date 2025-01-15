# ui/dialogs/order_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QComboBox, QPushButton, QMessageBox, QTableWidget,
                           QTableWidgetItem, QSpinBox)
from PyQt6.QtCore import Qt

class OrderDialog(QDialog):
    def __init__(self, db, order=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.order = order
        self.items = []  # Seznam položek objednávky
        self.init_ui()
        if order:
            self.load_order_data()

    def init_ui(self):
        self.setWindowTitle("Nová objednávka" if not self.order else "Upravit objednávku")
        self.setMinimumWidth(600)
        layout = QVBoxLayout(self)

        # Zákazník
        customer_layout = QHBoxLayout()
        customer_layout.addWidget(QLabel("Zákazník:"))
        self.customer_combo = QComboBox()
        self.load_customers()
        customer_layout.addWidget(self.customer_combo)
        layout.addLayout(customer_layout)

        # Status
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(['pending', 'processing', 'shipped', 'delivered', 'cancelled'])
        status_layout.addWidget(self.status_combo)
        layout.addLayout(status_layout)

        # Položky objednávky
        layout.addWidget(QLabel("Položky objednávky:"))
        
        # Tabulka položek
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(['ID', 'Produkt', 'Cena/ks', 'Množství', ''])
        layout.addWidget(self.items_table)

        # Tlačítko pro přidání položky
        add_item_btn = QPushButton("Přidat položku")
        add_item_btn.clicked.connect(self.add_item)
        layout.addWidget(add_item_btn)

        # Celková cena
        self.total_label = QLabel("Celková cena: 0 Kč")
        layout.addWidget(self.total_label)

        # Tlačítka
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Uložit")
        save_btn.clicked.connect(self.save_order)
        cancel_btn = QPushButton("Zrušit")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def load_customers(self):
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("""
                SELECT CustomerID, FirstName + ' ' + LastName as FullName 
                FROM Customers
            """)
            customers = cursor.fetchall()
            self.customer_combo.clear()
            self.customers = {name: id for id, name in customers}
            self.customer_combo.addItems(self.customers.keys())
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Nelze načíst zákazníky: {str(e)}")

    def add_item(self):
        dialog = OrderItemDialog(self.db, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            product_id, name, price = dialog.get_selected_product()
            self.add_item_to_table(product_id, name, price)
            self.update_total()

    def add_item_to_table(self, product_id, name, price):
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        
        # ID produktu
        id_item = QTableWidgetItem(str(product_id))
        id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.items_table.setItem(row, 0, id_item)
        
        # Název produktu
        name_item = QTableWidgetItem(name)
        name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.items_table.setItem(row, 1, name_item)
        
        # Cena
        price_item = QTableWidgetItem(f"{price:.2f} Kč")
        price_item.setFlags(price_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.items_table.setItem(row, 2, price_item)
        
        # Množství
        quantity_spin = QSpinBox()
        quantity_spin.setRange(1, 100)
        quantity_spin.setValue(1)
        quantity_spin.valueChanged.connect(self.update_total)
        self.items_table.setCellWidget(row, 3, quantity_spin)
        
        # Tlačítko pro smazání
        delete_btn = QPushButton("Odebrat")
        delete_btn.clicked.connect(lambda: self.remove_item(row))
        self.items_table.setCellWidget(row, 4, delete_btn)

    def remove_item(self, row):
        self.items_table.removeRow(row)
        self.update_total()

    def update_total(self):
        total = 0
        for row in range(self.items_table.rowCount()):
            price = float(self.items_table.item(row, 2).text().replace(" Kč", ""))
            quantity = self.items_table.cellWidget(row, 3).value()
            total += price * quantity
        self.total_label.setText(f"Celková cena: {total:.2f} Kč")

    def save_order(self):
        try:
            if self.items_table.rowCount() == 0:
                QMessageBox.warning(self, "Varování", "Objednávka musí obsahovat alespoň jednu položku")
                return

            customer_id = self.customers[self.customer_combo.currentText()]
            status = self.status_combo.currentText()
            total = float(self.total_label.text().split(":")[1].replace(" Kč", ""))

            cursor = self.db.connection.cursor()
            
            if self.order:  # Úprava existující objednávky
                cursor.execute("""
                    UPDATE Orders 
                    SET CustomerID = ?, Status = ?, TotalAmount = ?
                    WHERE OrderID = ?
                """, (customer_id, status, total, self.order))
                
                # Smazat staré položky
                cursor.execute("DELETE FROM OrderItems WHERE OrderID = ?", (self.order,))
            else:  # Nová objednávka
                cursor.execute("""
                    INSERT INTO Orders (CustomerID, Status, TotalAmount)
                    VALUES (?, ?, ?)
                """, (customer_id, status, total))
                self.order = cursor.execute("SELECT @@IDENTITY").fetchone()[0]

            # Vložit nové položky
            for row in range(self.items_table.rowCount()):
                product_id = int(self.items_table.item(row, 0).text())
                quantity = self.items_table.cellWidget(row, 3).value()
                price = float(self.items_table.item(row, 2).text().replace(" Kč", ""))
                
                cursor.execute("""
                    INSERT INTO OrderItems (OrderID, ProductID, Quantity, UnitPrice)
                    VALUES (?, ?, ?, ?)
                """, (self.order, product_id, quantity, price))

            self.db.connection.commit()
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Nelze uložit objednávku: {str(e)}")

class OrderItemDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Přidat položku")
        layout = QVBoxLayout(self)

        # Výběr produktu
        layout.addWidget(QLabel("Produkt:"))
        self.product_combo = QComboBox()
        self.load_products()
        layout.addWidget(self.product_combo)

        # Tlačítka
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Zrušit")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def load_products(self):
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("""
                SELECT ProductID, Name, Price 
                FROM Products 
                WHERE Status = 'available' AND StockQuantity > 0
            """)
            self.products = cursor.fetchall()
            self.product_combo.clear()
            self.product_combo.addItems([f"{p[1]} ({p[2]:.2f} Kč)" for p in self.products])
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Nelze načíst produkty: {str(e)}")

    def get_selected_product(self):
        index = self.product_combo.currentIndex()
        if index >= 0:
            return self.products[index]
        return None