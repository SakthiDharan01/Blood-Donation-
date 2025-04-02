import mysql.connector
from mysql.connector import Error
from tabulate import tabulate
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseOperations:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                database=os.getenv('DB_NAME', 'blood_donation_system')
            )
            self.cursor = self.connection.cursor(dictionary=True)
        except Error as e:
            print(f"Error connecting to MySQL Database: {e}")
            raise

    def close_connection(self):
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()

    # Donor Operations
    def add_donor(self, name, age, blood_group, contact_number, email, address):
        try:
            query = """
            INSERT INTO donors (name, age, blood_group, contact_number, email, address)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (name, age, blood_group, contact_number, email, address)
            self.cursor.execute(query, values)
            self.connection.commit()
            return self.cursor.lastrowid
        except Error as e:
            print(f"Error adding donor: {e}")
            self.connection.rollback()
            raise

    def search_donors(self, blood_group=None, location=None):
        try:
            query = "SELECT * FROM donors WHERE 1=1"
            values = []
            
            if blood_group:
                query += " AND blood_group = %s"
                values.append(blood_group)
            if location:
                query += " AND address LIKE %s"
                values.append(f"%{location}%")
            
            self.cursor.execute(query, values)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error searching donors: {e}")
            raise

    # Blood Bank Operations
    def add_blood_bank(self, name, address, contact_number, email):
        try:
            query = """
            INSERT INTO blood_banks (name, address, contact_number, email)
            VALUES (%s, %s, %s, %s)
            """
            values = (name, address, contact_number, email)
            self.cursor.execute(query, values)
            self.connection.commit()
            return self.cursor.lastrowid
        except Error as e:
            print(f"Error adding blood bank: {e}")
            self.connection.rollback()
            raise

    def get_blood_bank_inventory(self, bank_id=None):
        try:
            query = """
            SELECT bb.name, bi.blood_group, bi.quantity, bi.last_updated
            FROM blood_banks bb
            JOIN blood_inventory bi ON bb.bank_id = bi.bank_id
            """
            if bank_id:
                query += " WHERE bb.bank_id = %s"
                self.cursor.execute(query, (bank_id,))
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error getting blood bank inventory: {e}")
            raise

    # Recipient Operations
    def add_recipient(self, name, blood_group, contact_number, hospital_name, 
                     hospital_address, urgency_level, units_needed):
        try:
            query = """
            INSERT INTO recipients (name, blood_group, contact_number, hospital_name,
                                  hospital_address, urgency_level, units_needed)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (name, blood_group, contact_number, hospital_name,
                     hospital_address, urgency_level, units_needed)
            self.cursor.execute(query, values)
            self.connection.commit()
            return self.cursor.lastrowid
        except Error as e:
            print(f"Error adding recipient: {e}")
            self.connection.rollback()
            raise

    def match_recipient(self, recipient_id):
        try:
            # Get recipient details
            query = "SELECT * FROM recipients WHERE recipient_id = %s"
            self.cursor.execute(query, (recipient_id,))
            recipient = self.cursor.fetchone()
            
            if not recipient:
                return None

            # Find matching blood banks with sufficient stock
            query = """
            SELECT bb.bank_id, bb.name, bb.address, bi.quantity
            FROM blood_banks bb
            JOIN blood_inventory bi ON bb.bank_id = bi.bank_id
            WHERE bi.blood_group = %s AND bi.quantity >= %s
            ORDER BY bi.quantity DESC
            """
            self.cursor.execute(query, (recipient['blood_group'], recipient['units_needed']))
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error matching recipient: {e}")
            raise

    # Transaction Operations
    def record_donation(self, donor_id, bank_id, blood_group, units):
        try:
            query = """
            INSERT INTO transactions (donor_id, bank_id, blood_group, units, transaction_type)
            VALUES (%s, %s, %s, %s, 'DONATION')
            """
            values = (donor_id, bank_id, blood_group, units)
            self.cursor.execute(query, values)
            self.connection.commit()
            return self.cursor.lastrowid
        except Error as e:
            print(f"Error recording donation: {e}")
            self.connection.rollback()
            raise

    def record_distribution(self, recipient_id, bank_id, blood_group, units):
        try:
            query = """
            INSERT INTO transactions (recipient_id, bank_id, blood_group, units, transaction_type)
            VALUES (%s, %s, %s, %s, 'DISTRIBUTION')
            """
            values = (recipient_id, bank_id, blood_group, units)
            self.cursor.execute(query, values)
            self.connection.commit()
            return self.cursor.lastrowid
        except Error as e:
            print(f"Error recording distribution: {e}")
            self.connection.rollback()
            raise

    # Report Generation
    def generate_donor_report(self, blood_group=None, start_date=None, end_date=None):
        try:
            query = """
            SELECT d.name, d.blood_group, d.address, t.transaction_date, t.units
            FROM donors d
            JOIN transactions t ON d.donor_id = t.donor_id
            WHERE t.transaction_type = 'DONATION'
            """
            values = []
            
            if blood_group:
                query += " AND d.blood_group = %s"
                values.append(blood_group)
            if start_date:
                query += " AND t.transaction_date >= %s"
                values.append(start_date)
            if end_date:
                query += " AND t.transaction_date <= %s"
                values.append(end_date)
            
            query += " ORDER BY t.transaction_date DESC"
            
            self.cursor.execute(query, values)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error generating donor report: {e}")
            raise

    def generate_inventory_report(self):
        try:
            query = """
            SELECT 
                bb.name AS bank_name,
                bi.blood_group,
                bi.quantity,
                CASE 
                    WHEN bi.quantity < 10 THEN 'LOW'
                    WHEN bi.quantity < 20 THEN 'MEDIUM'
                    ELSE 'SUFFICIENT'
                END AS stock_status
            FROM blood_banks bb
            JOIN blood_inventory bi ON bb.bank_id = bi.bank_id
            ORDER BY bb.name, bi.blood_group
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error generating inventory report: {e}")
            raise

    def generate_emergency_report(self):
        try:
            query = """
            SELECT 
                r.name,
                r.blood_group,
                r.hospital_name,
                r.urgency_level,
                r.units_needed,
                r.created_at
            FROM recipients r
            WHERE r.status = 'PENDING'
            ORDER BY 
                CASE r.urgency_level
                    WHEN 'CRITICAL' THEN 1
                    WHEN 'HIGH' THEN 2
                    WHEN 'MEDIUM' THEN 3
                    WHEN 'LOW' THEN 4
                END,
                r.created_at
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error generating emergency report: {e}")
            raise 