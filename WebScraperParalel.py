# paralel, 10x naključnih 5 url testov.
 
import sys
import time
import random
import requests
import numpy as np
from mpi4py import MPI
 
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
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    urls_file = sys.argv[1] if len(sys.argv) > 1 else "urls.txt"
    keyword = sys.argv[2] if len(sys.argv) > 2 else "fakulteta"
    n_runs = 10
    sample_size = 5
 
    # Master prebere URLje
    if rank == 0:
        urls = read_urls(urls_file)
    else:
        urls = None
 
    # Broadcasta URLje vsem procesom
    urls = comm.bcast(urls, root=0)
    local_times = []
 
    for run in range(n_runs):
        comm.Barrier()
        start = MPI.Wtime()
 
        # Naključno izbere 5 URLjev (vsi procesi izberejo enak vzorec)
        sample_urls = random.sample(urls, sample_size)
 
        # Vsak proces obdeluje svoj kos: razdelitev po indeksih
        chunk_size = len(sample_urls) // size
        start_idx = rank * chunk_size

        # Zadnji proces pobere vse preostale URLje
        if rank == size - 1:
            end_idx = len(sample_urls)
        else:
            end_idx = (rank + 1) * chunk_size
 
        local_urls = sample_urls[start_idx:end_idx]
 
        # Obdelava lokalnega kosa
        for url in local_urls:
            check_url(url, keyword)
 
        comm.Barrier()
        elapsed = MPI.Wtime() - start

        # Zberi maksimalni čas med vsemi procesi
        max_time = comm.reduce(elapsed, op=MPI.MAX, root=0)
 
        if rank == 0:
            local_times.append(max_time)
            print(f"Run {run+1:2d}: {max_time:.4f} s")

    if rank == 0:
        times = np.array(local_times)

        print("\n--- Povzetek časa ---")
        print(f"Povprečni čas: {times.mean():.4f} s")
        print(f"Standardni odklon: {times.std():.4f} s")
        print(f"Minimalni čas: {times.min():.4f} s")
        print(f"Maximalni čas: {times.max():.4f} s")
 
if __name__ == "__main__":
    main()
 