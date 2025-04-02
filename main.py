from database_operations import DatabaseOperations
from tabulate import tabulate
import os
from datetime import datetime

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu():
    print("\n=== Blood Donation Management System ===")
    print("1. Donor Management")
    print("2. Blood Bank Management")
    print("3. Recipient Management")
    print("4. Reports")
    print("5. Exit")
    print("\nEnter your choice (1-5): ")

def donor_menu(db):
    while True:
        clear_screen()
        print("\n=== Donor Management ===")
        print("1. Add New Donor")
        print("2. Search Donors")
        print("3. Back to Main Menu")
        print("\nEnter your choice (1-3): ")
        
        choice = input()
        
        if choice == '1':
            clear_screen()
            print("\n=== Add New Donor ===")
            name = input("Enter donor name: ")
            age = int(input("Enter donor age: "))
            blood_group = input("Enter blood group (A+/A-/B+/B-/AB+/AB-/O+/O-): ")
            contact_number = input("Enter contact number: ")
            email = input("Enter email: ")
            address = input("Enter address: ")
            
            try:
                donor_id = db.add_donor(name, age, blood_group, contact_number, email, address)
                print(f"\nDonor added successfully! Donor ID: {donor_id}")
            except Exception as e:
                print(f"\nError adding donor: {e}")
            
            input("\nPress Enter to continue...")
            
        elif choice == '2':
            clear_screen()
            print("\n=== Search Donors ===")
            blood_group = input("Enter blood group to search (press Enter to skip): ")
            location = input("Enter location to search (press Enter to skip): ")
            
            try:
                donors = db.search_donors(blood_group if blood_group else None,
                                        location if location else None)
                if donors:
                    print("\nSearch Results:")
                    print(tabulate(donors, headers="keys", tablefmt="grid"))
                else:
                    print("\nNo donors found matching the criteria.")
            except Exception as e:
                print(f"\nError searching donors: {e}")
            
            input("\nPress Enter to continue...")
            
        elif choice == '3':
            break

def blood_bank_menu(db):
    while True:
        clear_screen()
        print("\n=== Blood Bank Management ===")
        print("1. Add New Blood Bank")
        print("2. View Blood Bank Inventory")
        print("3. Back to Main Menu")
        print("\nEnter your choice (1-3): ")
        
        choice = input()
        
        if choice == '1':
            clear_screen()
            print("\n=== Add New Blood Bank ===")
            name = input("Enter blood bank name: ")
            address = input("Enter address: ")
            contact_number = input("Enter contact number: ")
            email = input("Enter email: ")
            
            try:
                bank_id = db.add_blood_bank(name, address, contact_number, email)
                print(f"\nBlood bank added successfully! Bank ID: {bank_id}")
            except Exception as e:
                print(f"\nError adding blood bank: {e}")
            
            input("\nPress Enter to continue...")
            
        elif choice == '2':
            clear_screen()
            print("\n=== Blood Bank Inventory ===")
            bank_id = input("Enter blood bank ID (press Enter to view all): ")
            
            try:
                inventory = db.get_blood_bank_inventory(int(bank_id) if bank_id else None)
                if inventory:
                    print("\nInventory Status:")
                    print(tabulate(inventory, headers="keys", tablefmt="grid"))
                else:
                    print("\nNo inventory data found.")
            except Exception as e:
                print(f"\nError viewing inventory: {e}")
            
            input("\nPress Enter to continue...")
            
        elif choice == '3':
            break

def recipient_menu(db):
    while True:
        clear_screen()
        print("\n=== Recipient Management ===")
        print("1. Add New Recipient")
        print("2. Match Recipient with Blood Bank")
        print("3. Back to Main Menu")
        print("\nEnter your choice (1-3): ")
        
        choice = input()
        
        if choice == '1':
            clear_screen()
            print("\n=== Add New Recipient ===")
            name = input("Enter recipient name: ")
            blood_group = input("Enter blood group needed (A+/A-/B+/B-/AB+/AB-/O+/O-): ")
            contact_number = input("Enter contact number: ")
            hospital_name = input("Enter hospital name: ")
            hospital_address = input("Enter hospital address: ")
            urgency_level = input("Enter urgency level (LOW/MEDIUM/HIGH/CRITICAL): ")
            units_needed = int(input("Enter units needed: "))
            
            try:
                recipient_id = db.add_recipient(name, blood_group, contact_number,
                                              hospital_name, hospital_address,
                                              urgency_level, units_needed)
                print(f"\nRecipient added successfully! Recipient ID: {recipient_id}")
            except Exception as e:
                print(f"\nError adding recipient: {e}")
            
            input("\nPress Enter to continue...")
            
        elif choice == '2':
            clear_screen()
            print("\n=== Match Recipient with Blood Bank ===")
            recipient_id = input("Enter recipient ID: ")
            
            try:
                matches = db.match_recipient(int(recipient_id))
                if matches:
                    print("\nMatching Blood Banks:")
                    print(tabulate(matches, headers="keys", tablefmt="grid"))
                else:
                    print("\nNo matching blood banks found with sufficient stock.")
            except Exception as e:
                print(f"\nError matching recipient: {e}")
            
            input("\nPress Enter to continue...")
            
        elif choice == '3':
            break

def reports_menu(db):
    while True:
        clear_screen()
        print("\n=== Reports ===")
        print("1. Donor Activity Report")
        print("2. Inventory Status Report")
        print("3. Emergency Requests Report")
        print("4. Back to Main Menu")
        print("\nEnter your choice (1-4): ")
        
        choice = input()
        
        if choice == '1':
            clear_screen()
            print("\n=== Donor Activity Report ===")
            blood_group = input("Enter blood group to filter (press Enter to skip): ")
            start_date = input("Enter start date (YYYY-MM-DD) (press Enter to skip): ")
            end_date = input("Enter end date (YYYY-MM-DD) (press Enter to skip): ")
            
            try:
                report = db.generate_donor_report(
                    blood_group if blood_group else None,
                    start_date if start_date else None,
                    end_date if end_date else None
                )
                if report:
                    print("\nDonor Activity Report:")
                    print(tabulate(report, headers="keys", tablefmt="grid"))
                else:
                    print("\nNo donor activity found for the specified criteria.")
            except Exception as e:
                print(f"\nError generating donor report: {e}")
            
            input("\nPress Enter to continue...")
            
        elif choice == '2':
            clear_screen()
            print("\n=== Inventory Status Report ===")
            
            try:
                report = db.generate_inventory_report()
                if report:
                    print("\nInventory Status Report:")
                    print(tabulate(report, headers="keys", tablefmt="grid"))
                else:
                    print("\nNo inventory data found.")
            except Exception as e:
                print(f"\nError generating inventory report: {e}")
            
            input("\nPress Enter to continue...")
            
        elif choice == '3':
            clear_screen()
            print("\n=== Emergency Requests Report ===")
            
            try:
                report = db.generate_emergency_report()
                if report:
                    print("\nEmergency Requests Report:")
                    print(tabulate(report, headers="keys", tablefmt="grid"))
                else:
                    print("\nNo pending emergency requests found.")
            except Exception as e:
                print(f"\nError generating emergency report: {e}")
            
            input("\nPress Enter to continue...")
            
        elif choice == '4':
            break

def main():
    try:
        db = DatabaseOperations()
        
        while True:
            clear_screen()
            print_menu()
            choice = input()
            
            if choice == '1':
                donor_menu(db)
            elif choice == '2':
                blood_bank_menu(db)
            elif choice == '3':
                recipient_menu(db)
            elif choice == '4':
                reports_menu(db)
            elif choice == '5':
                print("\nThank you for using the Blood Donation Management System!")
                break
            else:
                print("\nInvalid choice. Please try again.")
                input("\nPress Enter to continue...")
        
        db.close_connection()
        
    except Exception as e:
        print(f"\nError: {e}")
        print("Please check your database connection and try again.")

if __name__ == "__main__":
    main() 