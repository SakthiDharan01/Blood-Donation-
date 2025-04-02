import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_database():
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            db_name = os.getenv('DB_NAME', 'blood_donation')
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            print(f"Database '{db_name}' created or already exists")
            
            # Switch to the database
            cursor.execute(f"USE {db_name}")
            
            # Read and execute schema.sql
            with open('schema.sql', 'r') as file:
                # Split the file into individual statements
                statements = file.read().split(';')
                
                # Execute each statement
                for statement in statements:
                    if statement.strip():
                        try:
                            # Handle DELIMITER statements
                            if statement.strip().upper().startswith('DELIMITER'):
                                continue  # Skip DELIMITER statements
                            cursor.execute(statement)
                        except Error as e:
                            # Skip duplicate key errors
                            if e.errno == 1061:  # Duplicate key error
                                print(f"Skipping duplicate key: {e}")
                                continue
                            # Skip table exists error
                            elif e.errno == 1050:  # Table exists error
                                print(f"Table already exists: {e}")
                                continue
                            else:
                                raise e
            
            print("Database setup completed successfully!")
            
            # Insert sample data
            insert_sample_data(cursor)
            
            connection.commit()
            
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

def insert_sample_data(cursor):
    # Insert sample blood banks
    blood_banks = [
        ('City Hospital Blood Bank', '123 Main St, City', '555-0101', 'citybank@hospital.com'),
        ('Regional Blood Center', '456 Health Ave, Town', '555-0102', 'regional@blood.com'),
        ('Community Blood Services', '789 Care Blvd, Village', '555-0103', 'community@blood.com')
    ]
    
    cursor.execute("SELECT COUNT(*) FROM blood_banks")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO blood_banks (name, address, contact_number, email)
            VALUES (%s, %s, %s, %s)
        """, blood_banks)
        print("Sample blood banks inserted successfully!")

if __name__ == "__main__":
    setup_database() 