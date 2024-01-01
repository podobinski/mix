import pandas as pd
import builtwith
import ssl
from collections import Counter
import threading
import time

ssl._create_default_https_context = ssl._create_unverified_context

def detect_cms(url, results, index, time_results):
    start_time = time.time()
    try:
        technologies = builtwith.builtwith(url)
        results[index] = ', '.join(technologies['cms']) if 'cms' in technologies else "CMS not detected"
    except Exception as e:
        results[index] = f"Error: {e}"
    finally:
        time_results[index] = round(time.time() - start_time, 2)

def read_ods(file_path):
    df = pd.read_excel(file_path, engine="odf", header=None)
    return df.iloc[:, 1].tolist()

def write_ods(input_file, output_file, cms_results, time_results):
    df = pd.read_excel(input_file, engine="odf", header=None)
    df[9], df[10] = cms_results + [""] * (len(df) - len(cms_results)), time_results + [""] * (len(df) - len(time_results))
    df.to_excel(output_file, index=False, header=False, engine="odf")

input_file, output_file = 'lista.ods', 'lista-result.ods'
urls = read_ods(input_file)
cms_results, time_results = [None] * len(urls), [None] * len(urls)

for index, url in enumerate(urls, start=1):
    print(f"Checking URL {index}: {url}")
    thread = threading.Thread(target=detect_cms, args=(url, cms_results, index-1, time_results))
    thread.start()
    thread.join(timeout=60)

    if cms_results[index-1] is None:
        cms_results[index-1], time_results[index-1] = "Skipped due to timeout", 'Timeout'
        print(f"Skipped URL {index} due to timeout")
    else:
        print(f"Result for URL {index}: {cms_results[index-1]}, Time taken: {time_results[index-1]}s")

write_ods(input_file, output_file, cms_results, time_results)
cms_counts = Counter(cms_results)
for cms, count in cms_counts.items():
    print(f"{cms}: {count} time(s) found")
