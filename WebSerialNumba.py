# Serijska verzija z Numba, 10x naključnih 5 url testov.

import sys
import time
import requests
import random
import numpy as np
from numba import njit

def read_urls(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

@njit(cache=True)
def contains_keyword(data, keyword):
    n = data.size
    m = keyword.size
    if m == 0:
        return True
    if m > n:
        return False
    for i in range(n - m + 1):
        ok = True
        for j in range(m):
            if data[i + j] != keyword[j]:
                ok = False
                break
        if ok:
            return True
    return False

def check_url_numba(url, keyword):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data_bytes = resp.content.lower()
        key_bytes = keyword.lower().encode("utf-8")
        data_array = np.frombuffer(data_bytes, dtype=np.uint8)
        key_array = np.frombuffer(key_bytes, dtype=np.uint8)
        return contains_keyword(data_array, key_array)
    except requests.RequestException:
        return False

def warm_up(keyword):
    sample = np.frombuffer(b"test fakulteta test", dtype=np.uint8)
    key = np.frombuffer(keyword.lower().encode("utf-8"), dtype=np.uint8)
    contains_keyword(sample, key)

def main():
    urls_file = sys.argv[1] if len(sys.argv) > 1 else "urls.txt"
    keyword = sys.argv[2] if len(sys.argv) > 2 else "fakulteta"

    urls = read_urls(urls_file)
    warm_up(keyword)

    n_runs = 10
    times = []

    for run in range(n_runs):
        sample_urls = random.sample(urls, 5)
        start = time.perf_counter()
        for url in sample_urls:
            check_url_numba(url, keyword)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        print(f"Run {run+1:2d}: {elapsed:.4f} s")

    times = np.array(times)
    print("\n--- Povzetek časa ---")
    print(f"Povprečni čas: {times.mean():.4f} s")
    print(f"Standardni odklon: {times.std():.4f} s")
    print(f"Minimalni čas: {times.min():.4f} s")
    print(f"Maximalni čas: {times.max():.4f} s")

if __name__ == "__main__":
    main()