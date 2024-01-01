import pandas as pd
import builtwith
import ssl
from collections import Counter
import threading
import time  # Import the time module

# Disable SSL verification (use with caution)
ssl._create_default_https_context = ssl._create_unverified_context

def detect_cms(url, results, index, time_results):
    start_time = time.time()  # Start the timer
    try:
        technologies = builtwith.builtwith(url)
        if 'cms' in technologies:
            results[index] = ', '.join(technologies['cms'])
        else:
            results[index] = "CMS not detected"
    except Exception as e:
        results[index] = f"Error: {e}"
    finally:
        end_time = time.time()  # End the timer
        time_results[index] = round(end_time - start_time, 2)  # Store the time taken

def read_ods(file_path):
    df = pd.read_excel(file_path, engine="odf", header=None)
    return df.iloc[:, 1].tolist()

def write_ods(input_file, output_file, cms_results, time_results):
    df = pd.read_excel(input_file, engine="odf", header=None)
    df[9] = cms_results + [""] * (len(df) - len(cms_results))  # Writing CMS results to 9th column (index 8)
    df[10] = time_results + [""] * (len(df) - len(time_results))  # Writing time results to 10th column (index 9)
    df.to_excel(output_file, index=False, header=False, engine="odf")

# File paths
input_file = 'lista.ods'
output_file = 'lista-result.ods'

# Read URLs from the second column
urls = read_ods(input_file)

# Detect CMS for each URL and print the URL with its sequence number and CMS result
cms_results = [None] * len(urls)
time_results = [None] * len(urls)  # List to store the time taken for each URL
for index, url in enumerate(urls, start=1):
    print(f"Checking URL {index}: {url}")

    # Start the thread to detect CMS
    thread = threading.Thread(target=detect_cms, args=(url, cms_results, index-1, time_results))
    thread.start()
    thread.join(timeout=60)  # Wait for 60 seconds

    if cms_results[index-1] is None:
        cms_results[index-1] = "Skipped due to timeout"
        time_results[index-1] = 'Timeout'
        print(f"Skipped URL {index} due to timeout")
    else:
        print(f"Result for URL {index}: {cms_results[index-1]}, Time taken: {time_results[index-1]}s")  # Print CMS result and time taken

# Write results to a new ODS file
write_ods(input_file, output_file, cms_results, time_results)

# Count occurrences of each CMS
cms_counts = Counter(cms_results)
for cms, count in cms_counts.items():
    print(f"{cms}: {count} time(s) found")
