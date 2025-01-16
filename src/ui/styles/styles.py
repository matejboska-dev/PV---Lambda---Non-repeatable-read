# ui/styles/styles.py

class Styles:
    # Barvy
    PRIMARY_COLOR = "#2962ff"  # Modrá
    SECONDARY_COLOR = "#3949ab"  # Tmavě modrá
    BACKGROUND_COLOR = "#f5f5f5"  # Světle šedá
    TEXT_COLOR = "#212121"  # Tmavě šedá
    ERROR_COLOR = "#f44336"  # Červená
    SUCCESS_COLOR = "#4caf50"  # Zelená
    WARNING_COLOR = "#ff9800"  # Oranžová

    @staticmethod
    def get_main_window_style():
        return """
        QMainWindow {
            background-color: #f5f5f5;
        }
        
        QStatusBar {
            background-color: #2962ff;
            color: white;
            padding: 5px;
            font-weight: bold;
        }
        """

    @staticmethod
    def get_tab_style():
        return """
        QTabWidget::pane {
            border: 1px solid #cccccc;
            background: white;
            border-radius: 4px;
        }

        QTabWidget::tab-bar {
            left: 5px;
        }

        QTabBar::tab {
            background: #e0e0e0;
            color: #424242;
            padding: 8px 12px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }

        QTabBar::tab:selected {
            background: #2962ff;
            color: white;
        }

        QTabBar::tab:hover:!selected {
            background: #90caf9;
        }
        """

    @staticmethod
    def get_button_style():
        return """
        QPushButton {
            background-color: #2962ff;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #1565c0;
        }

        QPushButton:pressed {
            background-color: #0d47a1;
        }

        QPushButton:disabled {
            background-color: #bbdefb;
            color: #78909c;
        }
        """

    @staticmethod
    def get_table_style():
        return """
        QTableWidget {
            background-color: white;
            alternate-background-color: #f5f5f5;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            gridline-color: #e0e0e0;
        }

        QTableWidget::item {
            padding: 5px;
        }

        QTableWidget::item:selected {
            background-color: #bbdefb;
            color: #212121;
        }

        QHeaderView::section {
            background-color: #2962ff;
            color: white;
            padding: 8px;
            border: none;
            font-weight: bold;
        }
        """

    @staticmethod
    def get_input_style():
        return """
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            padding: 8px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
        }

        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
            border: 2px solid #2962ff;
        }

        QComboBox::drop-down {
            border: none;
            width: 20px;
        }

        QComboBox::down-arrow {
            image: url(down_arrow.png);
            width: 12px;
            height: 12px;
        }
        """