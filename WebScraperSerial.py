# serial, 10x naključnih 5 url testov.

import sys
import time
import requests
import random
import numpy as np

PROCESS_COUNT = 1

def read_urls(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

def check_url(url, keyword):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return keyword.lower() in resp.text.lower()
    except requests.RequestException:
        return False

def main():
    urls_file = sys.argv[1] if len(sys.argv) > 1 else "urls.txt"
    keyword = sys.argv[2] if len(sys.argv) > 2 else "fakulteta"

    urls = read_urls(urls_file)

    n_runs = 10
    times = []

    for run in range(n_runs):
        sample_urls = random.sample(urls, 5)
        start = time.perf_counter()
        for url in sample_urls:
            check_url(url, keyword)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        print(f"Run {run+1:2d}: {elapsed:.4f} s")

    times = np.array(times)
    print("\n--- Povzetek časa ---")
    print(f"Povprecni cas: {times.mean():.4f} s")
    print(f"Standardni odklon: {times.std():.4f} s")
    print(f"Minimalni cas: {times.min():.4f} s")
    print(f"Maximalni cas: {times.max():.4f} s")

if __name__ == "__main__":
    main()