import pandas as pd
import builtwith
import ssl
from collections import Counter
import threading

# Disable SSL verification (use with caution)
ssl._create_default_https_context = ssl._create_unverified_context

def detect_cms(url, results, index):
    try:
        technologies = builtwith.builtwith(url)
        if 'cms' in technologies:
            results[index] = ', '.join(technologies['cms'])
        else:
            results[index] = "CMS not detected"
    except Exception as e:
        results[index] = f"Error: {e}"

def read_ods(file_path):
    df = pd.read_excel(file_path, engine="odf", header=None)
    return df.iloc[:, 1].tolist()

def write_ods(input_file, output_file, cms_results):
    df = pd.read_excel(input_file, engine="odf", header=None)
    df[9] = cms_results + [""] * (len(df) - len(cms_results))  # Writing to 9th column (index 8)
    df.to_excel(output_file, index=False, header=False, engine="odf")

# File paths
input_file = 'lista.ods'
output_file = 'lista-result.ods'

# Read URLs from the second column
urls = read_ods(input_file)

# Detect CMS for each URL and print the URL with its sequence number and CMS result
cms_results = [None] * len(urls)
for index, url in enumerate(urls, start=1):
    print(f"Checking URL {index}: {url}")

    # Start the thread to detect CMS
    thread = threading.Thread(target=detect_cms, args=(url, cms_results, index-1))
    thread.start()
    thread.join(timeout=60)  # Wait for 60 seconds

    if cms_results[index-1] is None:
        cms_results[index-1] = "Skipped due to timeout"
        print(f"Skipped URL {index} due to timeout")
    else:
        print(f"Result for URL {index}: {cms_results[index-1]}")  # Print CMS result

# Write results to a new ODS file
write_ods(input_file, output_file, cms_results)

# Count occurrences of each CMS
cms_counts = Counter(cms_results)
for cms, count in cms_counts.items():
    print(f"{cms}: {count} time(s) found")
