import pandas as pd
import builtwith
import ssl
from collections import Counter
import concurrent.futures

# Disable SSL verification (use with caution)
ssl._create_default_https_context = ssl._create_unverified_context

def detect_cms(url):
    try:
        technologies = builtwith.builtwith(url)
        if 'cms' in technologies:
            return ', '.join(technologies['cms'])
        else:
            return "CMS not detected"
    except Exception as e:
        return f"Error: {e}"

def read_ods(file_path):
    df = pd.read_excel(file_path, engine="odf", header=None)
    return df.iloc[:, 1].tolist()

def write_ods(input_file, output_file, cms_results):
    df = pd.read_excel(input_file, engine="odf", header=None)
    df[8] = cms_results + [""] * (len(df) - len(cms_results))
    df.to_excel(output_file, index=False, header=False, engine="odf")

def process_url(url, index):
    cms_result = detect_cms(url)
    print(f"URL {index} ({url}): {cms_result}")  # Print URL with its sequence number and CMS result
    return cms_result

# File paths
input_file = 'lista.ods'
output_file = 'lista-result.ods'

# Read URLs from the second column
urls = read_ods(input_file)

# Detect CMS for each URL concurrently
cms_results = []
with concurrent.futures.ThreadPoolExecutor() as executor:
    # Create a future for each URL
    future_to_url = {executor.submit(process_url, url, index): index for index, url in enumerate(urls, start=1)}

    for future in concurrent.futures.as_completed(future_to_url):
        cms_results.append(future.result())

# Write results to a new ODS file
write_ods(input_file, output_file, cms_results)

# Count occurrences of each CMS
cms_counts = Counter(cms_results)
for cms, count in cms_counts.items():
    print(f"{cms}: {count} time(s) found")
