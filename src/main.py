# main.py
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from database import Database

def main():
    app = QApplication(sys.argv)
    db = Database()
    
    try:
        if not db.connect():
            raise Exception("Nepodařilo se připojit k databázi")
        
        window = MainWindow(db)
        window.show()
        
        sys.exit(app.exec())
        
    except Exception as e:
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(None, "Chyba", f"Nastala chyba: {str(e)}")
        sys.exit(1)
    finally:
        if db:
            db.disconnect()

if __name__ == "__main__":
    main()