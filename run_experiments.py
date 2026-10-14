"""
Bagian C - Skrip eksperimen otomatis
Nama : Angga Nurdiansyah | NIM : 247006111184
Jalankan: python run_experiments.py   (satu folder dengan hybrid_file_analyzer.py)
Butuh   : pip install matplotlib
"""

import csv
import statistics

import matplotlib
matplotlib.use("Agg")                      
import matplotlib.pyplot as plt

from hybrid_file_analyzer import (NAMA, NIM, DEFAULT_IO_DELAY,
                                  get_files, run_serial, run_hybrid)

REPEAT = 3                                  
IO_DELAY = DEFAULT_IO_DELAY

# (thread, proses, jumlah data)
CONFIGS = [
    (2, 3, 1840),   
    (1, 3, 1840),   
    (4, 3, 1840),   
    (8, 3, 1840),   
    (2, 1, 1840),  
    (2, 2, 1840),   
    (2, 4, 1840),   
    (2, 3, 500),    
    (2, 3, 1000),  
    (4, 4, 1000),   
]


def median_time(fn, *args):
    return statistics.median(fn(*args)[1] for _ in range(REPEAT))


def main():
    get_files(max(c[2] for c in CONFIGS))  

    serial_cache = {}                       
    rows = []
    for no, (th, pr, n) in enumerate(CONFIGS, start=1):
        files = get_files(n)
        if n not in serial_cache:
            print(f"[baseline] serial untuk {n} file ...")
            serial_cache[n] = median_time(run_serial, files, IO_DELAY)
        t_par = median_time(run_hybrid, files, th, pr, IO_DELAY)
        speedup = serial_cache[n] / t_par
        eff = speedup / pr * 100
        rows.append((no, th, pr, n, t_par, speedup, eff))
        print(f"[{no:>2}/{len(CONFIGS)}] T={th} P={pr} N={n} -> "
              f"{t_par:.2f}s  speedup={speedup:.2f}  eff={eff:.1f}%")

    # ---- Tabel hasil ----
    print(f"\nHasil Eksperimen - {NAMA} ({NIM})")
    print(f"{'No':<4}{'Thread':<8}{'Process':<9}{'Data':<7}{'Waktu (s)':<11}{'Speedup':<9}{'Efisiensi (%)'}")
    for no, th, pr, n, t, s, e in rows:
        print(f"{no:<4}{th:<8}{pr:<9}{n:<7}{t:<11.2f}{s:<9.2f}{e:.1f}")

    with open("hasil_eksperimen.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["No", "Thread", "Process", "Data", "Waktu (s)", "Speedup", "Efisiensi (%)"])
        for no, th, pr, n, t, s, e in rows:
            w.writerow([no, th, pr, n, round(t, 3), round(s, 3), round(e, 2)])
    print("\nTabel disimpan: hasil_eksperimen.csv")

    # ---- Grafik 1: Waktu vs Jumlah Thread (proses=3, data=1840) ----
    g1 = sorted((r[1], r[4]) for r in rows if r[2] == 3 and r[3] == 1840)
    plt.figure(figsize=(6, 4))
    plt.plot([x for x, _ in g1], [y for _, y in g1], marker="o")
    plt.xlabel("Jumlah Thread"); plt.ylabel("Waktu (s)")
    plt.title("Waktu vs Jumlah Thread (Proses=3, Data=1840)")
    plt.grid(True); plt.tight_layout(); plt.savefig("grafik1_waktu_vs_thread.png", dpi=150); plt.close()

    # ---- Grafik 2: Waktu vs Jumlah Process (thread=2, data=1840) ----
    g2 = sorted((r[2], r[4]) for r in rows if r[1] == 2 and r[3] == 1840)
    plt.figure(figsize=(6, 4))
    plt.plot([x for x, _ in g2], [y for _, y in g2], marker="o", color="tab:orange")
    plt.xlabel("Jumlah Process"); plt.ylabel("Waktu (s)")
    plt.title("Waktu vs Jumlah Process (Thread=2, Data=1840)")
    plt.grid(True); plt.tight_layout(); plt.savefig("grafik2_waktu_vs_process.png", dpi=150); plt.close()

    # ---- Grafik 3: Speedup vs Konfigurasi ----
    labels = [f"#{r[0]}\nT{r[1]}/P{r[2]}\nN{r[3]}" for r in rows]
    plt.figure(figsize=(10, 4.5))
    plt.bar(labels, [r[5] for r in rows], color="tab:green")
    plt.axhline(1, color="gray", linestyle="--", linewidth=1)
    plt.xlabel("Konfigurasi (Thread / Process / Data)"); plt.ylabel("Speedup")
    plt.title("Speedup vs Konfigurasi")
    plt.grid(True, axis="y"); plt.tight_layout(); plt.savefig("grafik3_speedup_vs_konfigurasi.png", dpi=150); plt.close()

    print("Grafik disimpan: grafik1_*.png, grafik2_*.png, grafik3_*.png")


if __name__ == "__main__":
    main()