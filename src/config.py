# config.py
import configparser
import os

class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_path = os.path.join(os.path.dirname(__file__), 'config.conf')
        self.load_config()

    def load_config(self):
        """Load configuration from file"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found at {self.config_path}")
        
        self.config.read(self.config_path)

    def get_db_config(self):
        """Get database configuration"""
        try:
            return {
                'server': self.config.get('DATABASE', 'server'),
                'database': self.config.get('DATABASE', 'database'),
                'username': self.config.get('DATABASE', 'username'),
                'password': self.config.get('DATABASE', 'password'),
                'driver': self.config.get('DATABASE', 'driver')
            }
        except configparser.Error as e:
            raise Exception(f"Error reading database configuration: {str(e)}")

    def get_connection_string(self):
        """Get database connection string"""
        db_config = self.get_db_config()
        return (
            f"DRIVER={db_config['driver']};"
            f"SERVER={db_config['server']};"
            f"DATABASE={db_config['database']};"
            f"UID={db_config['username']};"
            f"PWD={db_config['password']}"
        )

    def get_isolation_level(self):
        """Get transaction isolation level"""
        return self.config.get('TRANSACTION', 'default_isolation_level')

    def get_connection_settings(self):
        """Get connection settings"""
        return {
            'retries': self.config.getint('SETTINGS', 'connection_retries'),
            'timeout': self.config.getint('SETTINGS', 'connection_timeout')
        }

# Example usage
if __name__ == "__main__":
    try:
        config = Config()
        print("Connection string:", config.get_connection_string())
        print("Isolation level:", config.get_isolation_level())
        print("Connection settings:", config.get_connection_settings())
    except Exception as e:
        print(f"Error: {str(e)}")