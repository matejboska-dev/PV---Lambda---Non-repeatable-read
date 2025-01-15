# ui/tabs/orders_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QMessageBox, QDialog)
from PyQt6.QtCore import Qt
from ui.dialogs.order_dialog import OrderDialog

class OrdersTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Horní panel s tlačítky
        button_layout = QHBoxLayout()
        
        self.new_order_btn = QPushButton("Nová objednávka")
        self.view_order_btn = QPushButton("Zobrazit detail")
        self.delete_order_btn = QPushButton("Smazat objednávku")
        
        self.new_order_btn.clicked.connect(self.add_order)
        self.view_order_btn.clicked.connect(self.view_order)
        self.delete_order_btn.clicked.connect(self.delete_order)
        
        button_layout.addWidget(self.new_order_btn)
        button_layout.addWidget(self.view_order_btn)
        button_layout.addWidget(self.delete_order_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Tabulka objednávek
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.table)

    def load_data(self):
        try:
            headers = ['ID', 'Zákazník', 'Datum', 'Celková částka', 'Status']
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)

            cursor = self.db.connection.cursor()
            cursor.execute("""
                SELECT o.OrderID, 
                       CONCAT(c.FirstName, ' ', c.LastName) as CustomerName,
                       o.OrderDate, 
                       o.TotalAmount,
                       o.Status
                FROM Orders o
                JOIN Customers c ON o.CustomerID = c.CustomerID
                ORDER BY o.OrderDate DESC
            """)
            
            data = cursor.fetchall()
            self.table.setRowCount(len(data))
            
            for row, item in enumerate(data):
                for col, value in enumerate(item):
                    if col == 3:  # částka
                        value = f"{value:.2f} Kč"
                    elif col == 2:  # datum
                        value = value.strftime("%d.%m.%Y %H:%M")
                    table_item = QTableWidgetItem(str(value))
                    table_item.setFlags(table_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(row, col, table_item)

            self.table.resizeColumnsToContents()
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Nepodařilo se načíst objednávky: {str(e)}")
            return False

    def add_order(self):
        dialog = OrderDialog(self.db, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            self.parent().status_bar.showMessage("Objednávka byla vytvořena")

    def view_order(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Varování", "Vyberte objednávku k zobrazení")
            return
            
        order_id = int(self.table.item(selected[0].row(), 0).text())
        dialog = OrderDialog(self.db, order_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            self.parent().status_bar.showMessage("Objednávka byla upravena")

    def delete_order(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Varování", "Vyberte objednávku ke smazání")
            return
            
        order_id = int(self.table.item(selected[0].row(), 0).text())
        
        reply = QMessageBox.question(self, "Potvrdit smazání",
                                   "Opravdu chcete smazat tuto objednávku?",
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
                                   
        if reply == QMessageBox.StandardButton.Yes:
            try:
                cursor = self.db.connection.cursor()
                
                # Nejdříve smažeme položky objednávky
                cursor.execute("DELETE FROM OrderItems WHERE OrderID = ?", (order_id,))
                
                # Potom smažeme samotnou objednávku
                cursor.execute("DELETE FROM Orders WHERE OrderID = ?", (order_id,))
                
                self.db.connection.commit()
                self.load_data()
                self.parent().status_bar.showMessage("Objednávka byla smazána")
            except Exception as e:
                self.db.connection.rollback()
                QMessageBox.critical(self, "Chyba", f"Nelze smazat objednávku: {str(e)}")

    def refresh_data(self):
        """Obnoví data v tabulce"""
        self.load_data()