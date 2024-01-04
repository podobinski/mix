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
    current_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO krs_data (krs_number, registry_type, data, timestamp) VALUES (?, ?, ?, ?)
    ''', (krs_number, registry_type, json.dumps(data), current_timestamp))
    conn.commit()
    conn.close()

def get_latest_entry(krs_number, registry_type):
    conn = sqlite3.connect('krs_records.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT data FROM krs_data 
        WHERE krs_number = ? AND registry_type = ?
        ORDER BY timestamp DESC
        LIMIT 1
    ''', (krs_number, registry_type))
    result = cursor.fetchone()
    conn.close()
    return json.loads(result[0]) if result else None

def has_data_changed(new_data, old_data):
    new_podmioty = new_data.get('odpis', {}).get('dane', {})
    old_podmioty = old_data.get('odpis', {}).get('dane', {})

    for key in new_podmioty.keys():
        if key not in old_podmioty or json.dumps(new_podmioty[key], sort_keys=True, ensure_ascii=False) != json.dumps(old_podmioty[key], sort_keys=True, ensure_ascii=False):
            return True
    return False

def download_current_krs_record(krs_numbers):
    for krs_number in krs_numbers:
        for registry in ['P', 'S']:
            api_url = f"https://api-krs.ms.gov.pl/api/krs/OdpisAktualny/{krs_number}?rejestr={registry}&format=json"
            response = requests.get(api_url)

            if response.status_code == 200:
                new_data = response.json()
                old_data = get_latest_entry(krs_number, registry)

                if not old_data or has_data_changed(new_data, old_data):
                    insert_krs_data(krs_number, registry, new_data)
                    print(f"New or updated KRS record for {krs_number} in registry {registry} has been downloaded and saved.")
                else:
                    print(f"No changes for {krs_number} in registry {registry}. Record remains unchanged.")
            else:
                print(f"Warning: No record found in registry {registry} for KRS {krs_number}.")

# Initialize database and tables
create_database()

# Example usage with multiple KRS numbers
krs_numbers = ['0000198645', '0000030897']
download_current_krs_record(krs_numbers)
