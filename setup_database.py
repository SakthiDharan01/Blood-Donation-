import mysql.connector
from mysql.connector import Error

def setup_database():
    try:
        # Connect to MySQL server
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="hello"  # Updated password
        )
        cursor = conn.cursor()

        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS blood_donation")
        print("Database 'blood_donation' created or already exists")

        # Switch to the database
        cursor.execute("USE blood_donation")

        # Drop existing tables to ensure clean schema
        cursor.execute("DROP TABLE IF EXISTS transactions")
        cursor.execute("DROP TABLE IF EXISTS blood_inventory")
        cursor.execute("DROP TABLE IF EXISTS recipients")
        cursor.execute("DROP TABLE IF EXISTS donors")
        cursor.execute("DROP TABLE IF EXISTS blood_banks")

        # Create recipients table first
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipients (
                recipient_id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                age INT CHECK (age >= 0 AND age <= 120),
                blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
                contact_number VARCHAR(15) NOT NULL,
                hospital_name VARCHAR(100) NOT NULL,
                hospital_address TEXT NOT NULL,
                urgency_level ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') NOT NULL,
                units_needed INT NOT NULL,
                status ENUM('PENDING', 'FULFILLED', 'CANCELLED') DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)

        # Read and execute remaining schema.sql
        with open('schema.sql', 'r') as file:
            sql_commands = file.read()
            for command in sql_commands.split(';'):
                if command.strip() and 'CREATE TABLE IF NOT EXISTS recipients' not in command:
                    try:
                        cursor.execute(command)
                    except mysql.connector.Error as err:
                        if err.errno == 1061:  # Duplicate key error
                            print(f"Skipping duplicate key: {err}")
                        else:
                            print(f"Error executing command: {err}")
                            print(f"Command: {command}")

        # Check if blood banks exist
        cursor.execute("SELECT COUNT(*) FROM blood_banks")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Insert sample blood banks
            sample_banks = [
                ("City Hospital Blood Bank", "123 Main Street, City", "555-0101", "city@bloodbank.com"),
                ("General Hospital Blood Center", "456 Health Avenue, Town", "555-0102", "general@bloodbank.com"),
                ("Community Blood Services", "789 Care Road, Village", "555-0103", "community@bloodbank.com")
            ]
            cursor.executemany("""
                INSERT INTO blood_banks (name, address, contact_number, email)
                VALUES (%s, %s, %s, %s)
            """, sample_banks)
            print("Sample blood banks added successfully")

        conn.commit()
        print("Database setup completed successfully")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    setup_database() 