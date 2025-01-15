# ui/tabs/settings_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLabel, QComboBox,
                           QFileDialog, QMessageBox)
import json
import csv
import xml.etree.ElementTree as ET
from datetime import datetime

# ui/tabs/settings_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLabel, QComboBox,
                           QFileDialog, QMessageBox, QGroupBox)
import json
import os

class SettingsTab(QWidget):
    def __init__(self, db, main_window):
        super().__init__()
        self.db = db
        self.main_window = main_window
        self.settings_file = "settings.json"
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Sekce pro izolační úrovně transakcí
        isolation_group = QGroupBox("Nastavení izolační úrovně transakcí")
        isolation_layout = QVBoxLayout()

        # ComboBox pro výběr izolační úrovně
        self.isolation_label = QLabel("Výchozí izolační úroveň:")
        self.isolation_combo = QComboBox()
        self.isolation_combo.addItems([
            "READ UNCOMMITTED",
            "READ COMMITTED",
            "REPEATABLE READ",
            "SERIALIZABLE"
        ])
        self.isolation_combo.currentTextChanged.connect(self.change_isolation_level)

        # Přidání vysvětlujícího textu
        self.explanation_label = QLabel()
        self.update_explanation()
        self.isolation_combo.currentTextChanged.connect(self.update_explanation)

        isolation_layout.addWidget(self.isolation_label)
        isolation_layout.addWidget(self.isolation_combo)
        isolation_layout.addWidget(self.explanation_label)
        isolation_group.setLayout(isolation_layout)
        layout.addWidget(isolation_group)

        # Tlačítko pro uložení nastavení
        save_btn = QPushButton("Uložit nastavení")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        
        # Sekce pro import
        import_group = QVBoxLayout()
        import_label = QLabel("Import dat:")
        import_group.addWidget(import_label)
        
        # Import produktů
        import_products_btn = QPushButton("Import produktů")
        import_products_btn.clicked.connect(lambda: self.import_data("products"))
        import_group.addWidget(import_products_btn)
        
        # Import kategorií
        import_categories_btn = QPushButton("Import kategorií")
        import_categories_btn.clicked.connect(lambda: self.import_data("categories"))
        import_group.addWidget(import_categories_btn)
        
        layout.addLayout(import_group)
        
        # Sekce pro export
        export_group = QVBoxLayout()
        export_label = QLabel("Export dat:")
        export_group.addWidget(export_label)
        
        # Export produktů
        export_products_btn = QPushButton("Export produktů")
        export_products_btn.clicked.connect(lambda: self.export_data("products"))
        export_group.addWidget(export_products_btn)
        
        # Export kategorií
        export_categories_btn = QPushButton("Export kategorií")
        export_categories_btn.clicked.connect(lambda: self.export_data("categories"))
        export_group.addWidget(export_categories_btn)
        
        layout.addLayout(export_group)
        layout.addStretch()


    def import_data(self, data_type):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            f"Vyberte soubor pro import {data_type}",
            "",
            "CSV soubory (*.csv);;JSON soubory (*.json);;XML soubory (*.xml)"
        )
        
        if not file_name:
            return
            
        try:
            file_extension = file_name.split('.')[-1].lower()
            
            if file_extension == 'csv':
                self.import_from_csv(file_name, data_type)
            elif file_extension == 'json':
                self.import_from_json(file_name, data_type)
            elif file_extension == 'xml':
                self.import_from_xml(file_name, data_type)
                
            self.main_window.status_bar.showMessage(f"Data byla úspěšně importována")
            # Obnovení dat v příslušné záložce
            if data_type == "products":
                self.main_window.products_tab.load_data()
            elif data_type == "categories":
                self.main_window.categories_tab.load_data()
                
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Chyba při importu: {str(e)}")

    def export_data(self, data_type):
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            f"Uložit {data_type} jako",
            "",
            "CSV soubory (*.csv);;JSON soubory (*.json);;XML soubory (*.xml)"
        )
        
        if not file_name:
            return
            
        try:
            file_extension = file_name.split('.')[-1].lower()
            
            if file_extension == 'csv':
                self.export_to_csv(file_name, data_type)
            elif file_extension == 'json':
                self.export_to_json(file_name, data_type)
            elif file_extension == 'xml':
                self.export_to_xml(file_name, data_type)
                
            self.main_window.status_bar.showMessage(f"Data byla úspěšně exportována")
                
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Chyba při exportu: {str(e)}")

    def import_from_csv(self, file_name, data_type):
        with open(file_name, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            cursor = self.db.connection.cursor()
            
            if data_type == "products":
                for row in reader:
                    cursor.execute("""
                        INSERT INTO Products (CategoryID, Name, Price, StockQuantity, Status)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        int(row['CategoryID']),
                        row['Name'],
                        float(row['Price']),
                        int(row['StockQuantity']),
                        row['Status']
                    ))
            
            elif data_type == "categories":
                for row in reader:
                    cursor.execute("""
                        INSERT INTO Categories (Name, Description, IsActive)
                        VALUES (?, ?, ?)
                    """, (
                        row['Name'],
                        row['Description'],
                        row['IsActive'].lower() == 'true'
                    ))
            
            self.db.connection.commit()

    def export_to_csv(self, file_name, data_type):
        cursor = self.db.connection.cursor()
        
        if data_type == "products":
            cursor.execute("""
                SELECT p.CategoryID, p.Name, p.Price, p.StockQuantity, p.Status
                FROM Products p
            """)
            fieldnames = ['CategoryID', 'Name', 'Price', 'StockQuantity', 'Status']
            
        elif data_type == "categories":
            cursor.execute("""
                SELECT Name, Description, IsActive
                FROM Categories
            """)
            fieldnames = ['Name', 'Description', 'IsActive']
        
        rows = cursor.fetchall()
        
        with open(file_name, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in rows:
                writer.writerow(dict(zip(fieldnames, row)))

    def import_from_json(self, file_name, data_type):
        with open(file_name, 'r', encoding='utf-8') as file:
            data = json.load(file)
            cursor = self.db.connection.cursor()
            
            if data_type == "products":
                for item in data:
                    cursor.execute("""
                        INSERT INTO Products (CategoryID, Name, Price, StockQuantity, Status)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        item['CategoryID'],
                        item['Name'],
                        item['Price'],
                        item['StockQuantity'],
                        item['Status']
                    ))
            
            elif data_type == "categories":
                for item in data:
                    cursor.execute("""
                        INSERT INTO Categories (Name, Description, IsActive)
                        VALUES (?, ?, ?)
                    """, (
                        item['Name'],
                        item['Description'],
                        item['IsActive']
                    ))
            
            self.db.connection.commit()

    def export_to_json(self, file_name, data_type):
        cursor = self.db.connection.cursor()
        
        if data_type == "products":
            cursor.execute("""
                SELECT CategoryID, Name, Price, StockQuantity, Status
                FROM Products
            """)
            columns = ['CategoryID', 'Name', 'Price', 'StockQuantity', 'Status']
            
        elif data_type == "categories":
            cursor.execute("""
                SELECT Name, Description, IsActive
                FROM Categories
            """)
            columns = ['Name', 'Description', 'IsActive']
        
        rows = cursor.fetchall()
        data = [dict(zip(columns, row)) for row in rows]
        
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    def import_from_xml(self, file_name, data_type):
        tree = ET.parse(file_name)
        root = tree.getroot()
        cursor = self.db.connection.cursor()
        
        if data_type == "products":
            for product in root.findall('product'):
                cursor.execute("""
                    INSERT INTO Products (CategoryID, Name, Price, StockQuantity, Status)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    int(product.find('CategoryID').text),
                    product.find('Name').text,
                    float(product.find('Price').text),
                    int(product.find('StockQuantity').text),
                    product.find('Status').text
                ))
        
        elif data_type == "categories":
            for category in root.findall('category'):
                cursor.execute("""
                    INSERT INTO Categories (Name, Description, IsActive)
                    VALUES (?, ?, ?)
                """, (
                    category.find('Name').text,
                    category.find('Description').text,
                    category.find('IsActive').text.lower() == 'true'
                ))
        
        self.db.connection.commit()

    def export_to_xml(self, file_name, data_type):
        cursor = self.db.connection.cursor()
        root = ET.Element("data")
        
        if data_type == "products":
            cursor.execute("""
                SELECT CategoryID, Name, Price, StockQuantity, Status
                FROM Products
            """)
            columns = ['CategoryID', 'Name', 'Price', 'StockQuantity', 'Status']
            
            for row in cursor.fetchall():
                product = ET.SubElement(root, "product")
                for col, value in zip(columns, row):
                    elem = ET.SubElement(product, col)
                    elem.text = str(value)
                    
        elif data_type == "categories":
            cursor.execute("""
                SELECT Name, Description, IsActive
                FROM Categories
            """)
            columns = ['Name', 'Description', 'IsActive']
            
            for row in cursor.fetchall():
                category = ET.SubElement(root, "category")
                for col, value in zip(columns, row):
                    elem = ET.SubElement(category, col)
                    elem.text = str(value)
        
        tree = ET.ElementTree(root)
        tree.write(file_name, encoding='utf-8', xml_declaration=True)
        
    def update_explanation(self):
        """Aktualizuje vysvětlující text podle vybrané izolační úrovně"""
        explanations = {
            "READ UNCOMMITTED": """
                Nejnižší úroveň izolace.
                - Umožňuje čtení nezapsaných změn
                - Může způsobit 'špinavé čtení'
                - Vhodné pouze pro nekritické operace
            """,
            "READ COMMITTED": """
                Standardní úroveň izolace.
                - Zabraňuje 'špinavému čtení'
                - Může dojít k neopakovatelnému čtení
                - Vhodné pro běžné operace
            """,
            "REPEATABLE READ": """
                Vyšší úroveň izolace.
                - Zabraňuje neopakovatelnému čtení
                - Stejná data při opakovaném čtení
                - Vhodné pro důležité transakce
            """,
            "SERIALIZABLE": """
                Nejvyšší úroveň izolace.
                - Plně sériové zpracování
                - Nejbezpečnější, ale nejpomalejší
                - Vhodné pro kritické transakce
            """
        }
        current_level = self.isolation_combo.currentText()
        self.explanation_label.setText(explanations[current_level])

    def change_isolation_level(self, level):
        """Změní izolační úroveň v databázi"""
        try:
            cursor = self.db.connection.cursor()
            cursor.execute(f"SET TRANSACTION ISOLATION LEVEL {level}")
            self.main_window.status_bar.showMessage(f"Izolační úroveň nastavena na: {level}")
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Nelze změnit izolační úroveň: {str(e)}")

    def load_settings(self):
        """Načte uložené nastavení"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    # Nastavení izolační úrovně
                    isolation_level = settings.get('isolation_level', 'READ COMMITTED')
                    self.isolation_combo.setCurrentText(isolation_level)
                    self.change_isolation_level(isolation_level)
        except Exception as e:
            QMessageBox.warning(self, "Varování", f"Nelze načíst nastavení: {str(e)}")

    def save_settings(self):
        """Uloží aktuální nastavení"""
        try:
            settings = {
                'isolation_level': self.isolation_combo.currentText()
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f)
            self.main_window.status_bar.showMessage("Nastavení bylo uloženo")
            
            # Přidáme popup s potvrzením
            QMessageBox.information(
                self,
                "Úspěch",
                "Nastavení bylo úspěšně uloženo!\n\nIzolační úroveň: " + self.isolation_combo.currentText()
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Nelze uložit nastavení: {str(e)}")    

    def get_current_isolation_level(self):
        """Vrátí aktuální izolační úroveň"""
        return self.isolation_combo.currentText()