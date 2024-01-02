import requests
import sqlite3
import json
from datetime import datetime, timezone

def create_database():
    conn = sqlite3.connect('krs_records.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS krs_data (
            krs_number TEXT,
            registry_type TEXT,
            data TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_krs_data(krs_number, registry_type, data):
    conn = sqlite3.connect('krs_records.db')
    cursor = conn.cursor()
    current_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")  # Convert timezone-aware datetime to string
    cursor.execute('''
        INSERT INTO krs_data (krs_number, registry_type, data, timestamp) VALUES (?, ?, ?, ?)
    ''', (krs_number, registry_type, json.dumps(data), current_timestamp))
    conn.commit()
    conn.close()

def download_current_krs_record(krs_numbers):
    for krs_number in krs_numbers:
        record_found = False
        registries = ['P', 'S']
        for registry in registries:
            api_url = f"https://api-krs.ms.gov.pl/api/krs/OdpisAktualny/{krs_number}?rejestr={registry}&format=json"
            response = requests.get(api_url)

            if response.status_code == 200:
                insert_krs_data(krs_number, registry, response.json())
                print(f"Current KRS record for {krs_number} in registry {registry} has been downloaded and saved to the database.")
                record_found = True
                break

        if not record_found:
            print(f"Warning: No record found in any registry for KRS {krs_number}.")

# Initialize database and tables
create_database()

# Example usage with multiple KRS numbers
krs_numbers = ['0000198645', '0000030897']
download_current_krs_record(krs_numbers)
