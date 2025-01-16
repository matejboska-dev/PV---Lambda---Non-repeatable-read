# ui/main_window.py

from PyQt6.QtWidgets import (QMainWindow, QWidget, QTabWidget, 
                           QVBoxLayout, QStatusBar, QMessageBox,
                           QPushButton)
from .tabs.products_tab import ProductsTab
from .tabs.categories_tab import CategoriesTab
from .tabs.orders_tab import OrdersTab
from .tabs.settings_tab import SettingsTab
from .styles.styles import Styles

class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        
        # Nejdřív vytvoříme status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Připraven")
        
        # Pak aplikujeme styly
        self.apply_styles()
        
        # Nakonec inicializujeme UI
        self.init_ui()
        
        # Teprve po inicializaci UI můžeme načíst data
        self.load_all_data()

    def apply_styles(self):
        """Aplikuje styly na hlavní okno"""
        self.setStyleSheet(Styles.get_main_window_style())
        
    def init_ui(self):
        """Inicializace uživatelského rozhraní"""
        self.setWindowTitle("E-shop Management System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Centrální widget a layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Vytvoření záložek
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(Styles.get_tab_style())
        
        # Inicializace jednotlivých záložek
        self.products_tab = ProductsTab(self.db, self)
        self.categories_tab = CategoriesTab(self.db, self)  
        self.orders_tab = OrdersTab(self.db, self)
        self.settings_tab = SettingsTab(self.db, self)
        
        # Aplikace stylů na tabulky a tlačítka
        for tab in [self.products_tab, self.categories_tab, self.orders_tab]:
            if hasattr(tab, 'table'):
                tab.table.setStyleSheet(Styles.get_table_style())
            for button in tab.findChildren(QPushButton):
                button.setStyleSheet(Styles.get_button_style())
        
        # Přidání záložek do TabWidget
        self.tabs.addTab(self.products_tab, "Produkty")
        self.tabs.addTab(self.categories_tab, "Kategorie")
        self.tabs.addTab(self.orders_tab, "Objednávky")
        self.tabs.addTab(self.settings_tab, "Nastavení")
        
        # Přidání TabWidget do hlavního layoutu
        layout.addWidget(self.tabs)

    def load_all_data(self):
        """Načte data do všech tabulek"""
        try:
            if self.products_tab.load_data():
                self.status_bar.showMessage("Produkty načteny")
            if self.categories_tab.load_data():
                self.status_bar.showMessage("Kategorie načteny")
            if self.orders_tab.load_data():
                self.status_bar.showMessage("Objednávky načteny")
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Chyba při načítání dat: {str(e)}")

    def refresh_data(self):
        """Obnoví data ve všech tabulkách"""
        self.load_all_data()

    def closeEvent(self, event):
        """Handler pro zavření aplikace"""
        try:
            if self.db.connection:
                self.db.connection.close()
                self.status_bar.showMessage("Databázové spojení ukončeno")
        except Exception as e:
            QMessageBox.warning(self, "Varování", 
                              f"Problém při ukončování databázového spojení: {str(e)}")
        event.accept()