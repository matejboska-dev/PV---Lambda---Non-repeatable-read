# database.py
import pyodbc
from config import Config

class Database:
    def __init__(self):
        self.config = Config()
        self.connection = None
        self.cursor = None

    def connect(self):
        """Connect to database"""
        try:
            # Get connection settings
            settings = self.config.get_connection_settings()
            
            # Try to connect with retries
            for attempt in range(settings['retries']):
                try:
                    self.connection = pyodbc.connect(
                        self.config.get_connection_string(),
                        timeout=settings['timeout']
                    )
                    self.cursor = self.connection.cursor()
                    
                    # Set isolation level
                    isolation_level = self.config.get_isolation_level()
                    self.cursor.execute(f"SET TRANSACTION ISOLATION LEVEL {isolation_level}")
                    
                    print(f"Connected to database (attempt {attempt + 1})")
                    return True
                except pyodbc.Error as e:
                    if attempt == settings['retries'] - 1:  # Last attempt
                        raise
                    print(f"Connection attempt {attempt + 1} failed, retrying...")
            
            return False
        except pyodbc.Error as e:
            print(f"Database connection error: {str(e)}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("Disconnected from database")

# Example usage
if __name__ == "__main__":
    db = Database()
    if db.connect():
        print("Successfully connected to database")
        db.disconnect()
    else:
        print("Failed to connect to database")