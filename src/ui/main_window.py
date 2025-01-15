# ui/main_window.py
from PyQt6.QtWidgets import QMainWindow, QWidget, QTabWidget, QVBoxLayout, QStatusBar
from .tabs.products_tab import ProductsTab
from .tabs.categories_tab import CategoriesTab
from .tabs.orders_tab import OrdersTab
from .tabs.settings_tab import SettingsTab

class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_all_data()

    def init_ui(self):
        self.setWindowTitle("E-shop Management System")
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Vytvoření záložek
        self.tabs = QTabWidget()
        
        # Inicializace jednotlivých záložek
        self.products_tab = ProductsTab(self.db, self)  
        self.categories_tab = CategoriesTab(self.db)
        self.orders_tab = OrdersTab(self.db)
        self.settings_tab = SettingsTab(self.db)
        
        # Přidání záložek do TabWidget
        self.tabs.addTab(self.products_tab, "Produkty")
        self.tabs.addTab(self.categories_tab, "Kategorie")
        self.tabs.addTab(self.orders_tab, "Objednávky")
        self.tabs.addTab(self.settings_tab, "Nastavení")
        
        layout.addWidget(self.tabs)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Připraven")

    def load_all_data(self):
        """Načte data do všech tabulek"""
        if self.products_tab.load_data():
            self.status_bar.showMessage("Produkty načteny")
        if self.categories_tab.load_data():
            self.status_bar.showMessage("Kategorie načteny")
        if self.orders_tab.load_data():
            self.status_bar.showMessage("Objednávky načteny")

    def refresh_data(self):
        """Obnoví data ve všech tabulkách"""
        self.load_all_data()