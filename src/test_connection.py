# test_connection.py
from config import Config
import pyodbc

def test_database_connection():
    """Test database connection and select data from Products table"""
    config = Config()
    
    try:
        # Try to connect
        print("Attempting to connect to database...")
        connection = pyodbc.connect(config.get_connection_string())
        cursor = connection.cursor()
        print("Successfully connected to database!")
        
        # Test basic select
        print("\nTesting simple SELECT...")
        cursor.execute("SELECT TOP 5 * FROM Products")
        columns = [column[0] for column in cursor.description]
        print("\nColumns in Products table:", columns)  # This will help us see available columns
        
        rows = cursor.fetchall()
        
        if rows:
            print("\nProducts found:")
            for row in rows:
                # Using index access to be safe
                print("-" * 30)
                for i, column in enumerate(columns):
                    print(f"{column}: {row[i]}")
        else:
            print("No products found in database")
            
        # Test categories
        print("\nTesting Categories...")
        cursor.execute("SELECT * FROM Categories")
        cat_columns = [column[0] for column in cursor.description]
        categories = cursor.fetchall()
        
        if categories:
            print("\nCategories found:")
            for category in categories:
                print("-" * 30)
                for i, column in enumerate(cat_columns):
                    print(f"{column}: {category[i]}")
        else:
            print("No categories found in database")
            
        # Close connection
        cursor.close()
        connection.close()
        print("\nConnection closed successfully")
        
    except pyodbc.Error as e:
        print(f"\nDatabase Error: {str(e)}")
    except Exception as e:
        print(f"\nUnexpected Error: {str(e)}")

if __name__ == "__main__":
    print("Database Connection Test Starting...")
    print("=" * 50)
    test_database_connection()
    print("=" * 50)
    print("Test Complete")