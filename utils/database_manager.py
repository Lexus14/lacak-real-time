#!/usr/bin/env python3
"""
Database Manager for Pegasus Lacak Nomor
Tool untuk mengelola database lokal (import, export, query)
"""

import sqlite3
import json
import csv
import sys
from datetime import datetime
from colorama import Fore, Style, init

init()

DATABASE_PATH = "data/local_database.db"

def print_colored(message, color="cyan"):
    """Print colored message."""
    colors = {
        "red": Fore.RED,
        "green": Fore.GREEN,
        "yellow": Fore.YELLOW,
        "cyan": Fore.CYAN
    }
    print(f"{colors.get(color, Fore.WHITE)}{message}{Style.RESET_ALL}")

def init_database():
    """Initialize database with schema."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS phone_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT UNIQUE NOT NULL,
                name TEXT,
                address TEXT,
                city TEXT,
                province TEXT,
                operator TEXT,
                last_updated TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nik_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nik TEXT UNIQUE NOT NULL,
                name TEXT,
                birth_date TEXT,
                gender TEXT,
                address TEXT,
                city TEXT,
                province TEXT,
                last_updated TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print_colored("[✓] Database initialized successfully!", "green")
        return True
    except Exception as e:
        print_colored(f"[!] Error initializing database: {str(e)}", "red")
        return False

def import_from_json(json_file):
    """Import phone records from JSON file."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        count = 0
        if isinstance(data, list):
            for record in data:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO phone_records 
                        (phone_number, name, address, city, province, operator, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        record.get('phone_number', ''),
                        record.get('name', ''),
                        record.get('address', ''),
                        record.get('city', ''),
                        record.get('province', ''),
                        record.get('operator', ''),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ))
                    count += 1
                except Exception as e:
                    print_colored(f"[!] Error importing record: {str(e)}", "yellow")
        
        conn.commit()
        conn.close()
        print_colored(f"[✓] Imported {count} records from {json_file}", "green")
        return True
    except Exception as e:
        print_colored(f"[!] Error importing from JSON: {str(e)}", "red")
        return False

def import_from_csv(csv_file):
    """Import phone records from CSV file."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        count = 0
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO phone_records 
                        (phone_number, name, address, city, province, operator, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row.get('phone_number', ''),
                        row.get('name', ''),
                        row.get('address', ''),
                        row.get('city', ''),
                        row.get('province', ''),
                        row.get('operator', ''),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ))
                    count += 1
                except Exception as e:
                    print_colored(f"[!] Error importing row: {str(e)}", "yellow")
        
        conn.commit()
        conn.close()
        print_colored(f"[✓] Imported {count} records from {csv_file}", "green")
        return True
    except Exception as e:
        print_colored(f"[!] Error importing from CSV: {str(e)}", "red")
        return False

def export_to_json(output_file):
    """Export all phone records to JSON."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM phone_records')
        rows = cursor.fetchall()
        
        records = []
        for row in rows:
            records.append({
                'id': row[0],
                'phone_number': row[1],
                'name': row[2],
                'address': row[3],
                'city': row[4],
                'province': row[5],
                'operator': row[6],
                'last_updated': row[7]
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=4, ensure_ascii=False)
        
        conn.close()
        print_colored(f"[✓] Exported {len(records)} records to {output_file}", "green")
        return True
    except Exception as e:
        print_colored(f"[!] Error exporting to JSON: {str(e)}", "red")
        return False

def query_phone(phone_number):
    """Query single phone number."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM phone_records WHERE phone_number = ?', (phone_number,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            print_colored("\n[✓] Record found:", "green")
            print(f"Phone Number: {row[1]}")
            print(f"Name: {row[2]}")
            print(f"Address: {row[3]}")
            print(f"City: {row[4]}")
            print(f"Province: {row[5]}")
            print(f"Operator: {row[6]}")
            print(f"Last Updated: {row[7]}")
            return True
        else:
            print_colored("\n[!] No record found for this phone number.", "yellow")
            return False
    except Exception as e:
        print_colored(f"[!] Error querying database: {str(e)}", "red")
        return False

def list_all_records(limit=10):
    """List all records in database."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM phone_records')
        total = cursor.fetchone()[0]
        
        cursor.execute(f'SELECT * FROM phone_records LIMIT {limit}')
        rows = cursor.fetchall()
        
        conn.close()
        
        print_colored(f"\n[i] Total records in database: {total}", "cyan")
        print_colored(f"[i] Showing first {min(limit, len(rows))} records:\n", "cyan")
        
        for row in rows:
            print(f"{row[1]:15} | {row[2]:20} | {row[4]:15}")
        
        return True
    except Exception as e:
        print_colored(f"[!] Error listing records: {str(e)}", "red")
        return False

def delete_record(phone_number):
    """Delete a phone record."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM phone_records WHERE phone_number = ?', (phone_number,))
        conn.commit()
        
        if cursor.rowcount > 0:
            print_colored(f"[✓] Deleted record for {phone_number}", "green")
        else:
            print_colored(f"[!] No record found for {phone_number}", "yellow")
        
        conn.close()
        return True
    except Exception as e:
        print_colored(f"[!] Error deleting record: {str(e)}", "red")
        return False

def clear_database():
    """Clear all records from database."""
    confirm = input(f"{Fore.YELLOW}[!] Are you sure you want to clear all records? (yes/no): {Style.RESET_ALL}")
    if confirm.lower() == 'yes':
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM phone_records')
            cursor.execute('DELETE FROM nik_records')
            conn.commit()
            conn.close()
            
            print_colored("[✓] Database cleared successfully!", "green")
            return True
        except Exception as e:
            print_colored(f"[!] Error clearing database: {str(e)}", "red")
            return False
    else:
        print_colored("[!] Operation cancelled.", "yellow")
        return False

def show_menu():
    """Show database manager menu."""
    print(f"\n{Fore.CYAN}{'='*70}")
    print("DATABASE MANAGER - Pegasus Lacak Nomor")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    print("1. Initialize Database")
    print("2. Import from JSON")
    print("3. Import from CSV")
    print("4. Export to JSON")
    print("5. Query Phone Number")
    print("6. List All Records")
    print("7. Delete Record")
    print("8. Clear Database")
    print("0. Exit")
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")

def main():
    """Main program loop."""
    while True:
        show_menu()
        choice = input(f"\n{Fore.YELLOW}Choose option (0-8): {Style.RESET_ALL}")
        
        if choice == '1':
            init_database()
        elif choice == '2':
            file_path = input("Enter JSON file path: ")
            import_from_json(file_path)
        elif choice == '3':
            file_path = input("Enter CSV file path: ")
            import_from_csv(file_path)
        elif choice == '4':
            file_path = input("Enter output file path: ")
            export_to_json(file_path)
        elif choice == '5':
            phone = input("Enter phone number: ")
            query_phone(phone)
        elif choice == '6':
            limit = input("Enter limit (default 10): ") or "10"
            list_all_records(int(limit))
        elif choice == '7':
            phone = input("Enter phone number to delete: ")
            delete_record(phone)
        elif choice == '8':
            clear_database()
        elif choice == '0':
            print_colored("\n[i] Goodbye!", "cyan")
            sys.exit(0)
        else:
            print_colored("[!] Invalid option!", "red")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
