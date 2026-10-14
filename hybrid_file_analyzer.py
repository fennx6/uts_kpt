"""
UTS Komputasi Paralel dan Terdistribusi - Hybrid Computing
Proyek : Parallel File Analyzer (ThreadPool untuk I/O + ProcessPool untuk CPU)
Nama   : Angga Nurdiansyah
NIM    : 247006111184

Cara pakai:
    python hybrid_file_analyzer.py                       # konfigurasi default (dari NIM)
    python hybrid_file_analyzer.py --threads 4 --procs 2 --data 1000
"""

import argparse
import os
import random
import shutil
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

NAMA = "Angga Nurdiansyah"
NIM = "247006111184"

NIM_INT = int(NIM)
DEFAULT_THREADS = int(NIM[-2:]) % 4 + 2      # 84  mod 4 + 2 = 2
DEFAULT_PROCS = int(NIM[5:7]) % 3 + 2        # 61  mod 3 + 2 = 3  (digit ke-6 & ke-7)
DEFAULT_DATA = int(NIM[-3:]) * 10            # 184 x 10      = 1840

DEFAULT_IO_DELAY = 0.005   # detik simulasi latensi penyimpanan per file (I/O lambat)
DATASET_ROOT = "dataset"

VOWELS = frozenset("aeiouAEIOU")
VOCAB = (
    "komputasi paralel terdistribusi thread proses memori jaringan data "
    "universitas siliwangi informatika mahasiswa dosen ujian tengah semester "
    "algoritma sistem operasi prosesor kinerja kecepatan efisiensi analisis "
    "parallel computing hybrid pool worker task queue speedup throughput "
    "2026 247 1840 3.14 42 100 7 99 "
    "# @ & % ! ? + = * /"
).split()


# ----------------------------------------------------------------------------
# 1. Pembuatan dataset (deterministik: random.seed(NIM))
# ----------------------------------------------------------------------------
def generate_dataset(n_files, folder):
    """Buat n_files file teks acak. Isi selalu sama karena seed = NIM."""
    random.seed(NIM_INT)  
    rng = random.Random(NIM_INT)
    if os.path.isdir(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)
    for i in range(n_files):
        n_words = rng.randint(2000, 6000)
        words = rng.choices(VOCAB, k=n_words)
        lines = [" ".join(words[j:j + 12]) for j in range(0, n_words, 12)]
        with open(os.path.join(folder, f"doc_{i:05d}.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


def get_files(n_files):
    folder = os.path.join(DATASET_ROOT, f"seed_{NIM}")
    existing = sorted(os.listdir(folder)) if os.path.isdir(folder) else []
    if len(existing) < n_files:
        print(f"[setup] Membuat dataset {n_files} file di '{folder}' ...")
        generate_dataset(n_files, folder)
        existing = sorted(os.listdir(folder))
    return [os.path.join(folder, name) for name in existing[:n_files]]


# ----------------------------------------------------------------------------
# 2. Tugas I/O (dijalankan THREAD) dan tugas CPU (dijalankan PROSES)
# ----------------------------------------------------------------------------
def read_file(path, io_delay):
    """Tugas I/O-bound: baca isi file (+ simulasi latensi disk/jaringan)."""
    if io_delay > 0:
        time.sleep(io_delay)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def analyze_text(text):
    """Tugas CPU-bound: hitung vokal, kata, angka, simbol, total karakter."""
    vowels = digits = symbols = 0
    for ch in text:
        if ch in VOWELS:
            vowels += 1
        elif ch.isdigit():
            digits += 1
        elif ch.isalpha() or ch.isspace():
            pass
        else:
            symbols += 1
    return (vowels, len(text.split()), digits, symbols, len(text))


def merge(results):
    """Agregasi hasil semua file menjadi satu statistik total."""
    total = [0, 0, 0, 0, 0]
    for r in results:
        for i, v in enumerate(r):
            total[i] += v
    return dict(zip(("vokal", "kata", "angka", "simbol", "karakter"), total))


def run_serial(files, io_delay):
    start = time.perf_counter()
    results = [analyze_text(read_file(p, io_delay)) for p in files]
    elapsed = time.perf_counter() - start
    return merge(results), elapsed


def run_hybrid(files, n_threads, n_procs, io_delay):
    """Thread membaca file, lalu langsung mengirim teksnya ke ProcessPool."""
    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=n_procs) as ppool:

        def io_then_cpu(path):
            text = read_file(path, io_delay)          # I/O di thread
            return ppool.submit(analyze_text, text)   # CPU di proses

        with ThreadPoolExecutor(max_workers=n_threads) as tpool:
            futures = list(tpool.map(io_then_cpu, files))
        results = [f.result() for f in futures]
    elapsed = time.perf_counter() - start
    return merge(results), elapsed


# ----------------------------------------------------------------------------
# 4. Program utama
# ----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Hybrid Parallel File Analyzer")
    parser.add_argument("--threads", type=int, default=DEFAULT_THREADS)
    parser.add_argument("--procs", type=int, default=DEFAULT_PROCS)
    parser.add_argument("--data", type=int, default=DEFAULT_DATA)
    parser.add_argument("--io-delay", type=float, default=DEFAULT_IO_DELAY,
                        help="simulasi latensi I/O per file (detik)")
    args = parser.parse_args()

    random.seed(NIM_INT)
    files = get_files(args.data)

    print("Menjalankan versi serial (baseline) ...")
    stat_serial, t_serial = run_serial(files, args.io_delay)

    print("Menjalankan versi hybrid (Thread + ProcessPool) ...")
    stat_par, t_par = run_hybrid(files, args.threads, args.procs, args.io_delay)

    speedup = t_serial / t_par
    efficiency = speedup / args.procs * 100
    throughput = len(files) / t_par

    print()
    print(f"Hybrid Project by: {NAMA} ({NIM})")
    print(f"Threads: {args.threads} | Processes: {args.procs} | Data: {len(files)}")
    print(f"Total Time: {t_par:.2f} s | Speedup: {speedup:.2f} | Efficiency: {efficiency:.1f}%")
    print(f"Serial Time: {t_serial:.2f} s | Throughput: {throughput:.1f} file/s")
    print("Hasil analisis (total semua file):")
    for k, v in stat_par.items():
        print(f"  - {k:<9}: {v:,}")
    print("Verifikasi hasil serial == paralel:", "OK" if stat_serial == stat_par else "BERBEDA!")


if __name__ == "__main__":
    main()