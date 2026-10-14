# Parallel File Analyzer

Program UTS ini membandingkan analisis file secara **serial** dengan pendekatan
hybrid:

- `ThreadPoolExecutor` dipakai untuk membaca file (bagian I/O).
- `ProcessPoolExecutor` dipakai untuk menganalisis isi teks (bagian CPU).

Setiap file dianalisis untuk menghitung jumlah vokal, kata, angka, simbol, dan
karakter.

## Persiapan

Buka PowerShell, lalu masuk ke folder ini:

```powershell
cd "E:\KULIAH\SEMESTER 5\KOMPUTASI PARALEL\uts"
```

Gunakan Python 3.10 atau yang lebih baru. Install satu dependensi untuk skrip
eksperimen:

```powershell
python -m pip install matplotlib
```

Jika perintah `python` tidak tersedia di Windows, gunakan launcher berikut:

```powershell
py -m pip install matplotlib
```

## Menjalankan satu analisis

Jalankan konfigurasi default dengan:

```powershell
python hybrid_file_analyzer.py
```

Default yang digunakan program saat ini:

| Parameter | Nilai |
|---|---:|
| Thread | 2 |
| Process | 3 |
| Data | 1840 file |
| Simulasi delay I/O | 0.005 detik per file |

Konfigurasi dapat diubah melalui argumen:

```powershell
python hybrid_file_analyzer.py --threads 4 --procs 2 --data 1000
```

Untuk mengubah simulasi latensi I/O, tambahkan `--io-delay`. Nilai `0`
menonaktifkan delay:

```powershell
python hybrid_file_analyzer.py --threads 4 --procs 2 --data 1000 --io-delay 0
```

Output terminal menampilkan waktu serial, waktu hybrid, speedup, efisiensi,
throughput, total statistik, serta verifikasi bahwa hasil serial dan hybrid
sama.

## Menjalankan eksperimen otomatis

Skrip eksperimen mengulang setiap pengukuran tiga kali dan memakai nilai median
agar hasil tidak terlalu dipengaruhi variasi waktu sesaat:

```powershell
python run_experiments.py
```

Konfigurasi yang diuji ditentukan langsung di `run_experiments.py` dan saat ini
meliputi variasi:

- jumlah thread: 1, 2, 4, dan 8;
- jumlah process: 1, 2, 3, dan 4;
- jumlah data: 500, 1000, dan 1840 file.

Skrip ini menghasilkan atau menimpa file berikut di folder `uts`:

| File | Isi |
|---|---|
| `hasil_eksperimen.csv` | Tabel waktu, speedup, dan efisiensi setiap konfigurasi |
| `grafik1_waktu_vs_thread.png` | Waktu terhadap jumlah thread |
| `grafik2_waktu_vs_process.png` | Waktu terhadap jumlah process |
| `grafik3_speedup_vs_konfigurasi.png` | Speedup semua konfigurasi |

## Dataset

Dataset tidak perlu disiapkan secara manual. Saat program dijalankan, fungsi
`get_files()` mencari data di:

```text
dataset\seed_247006111184\
```

Jika jumlah file belum mencukupi, program membuat dataset teks secara
deterministik menggunakan seed dari NIM. Karena itu, isi dataset yang dibuat
ulang akan konsisten untuk NIM yang sama.

Perhatian: `generate_dataset()` menghapus folder dataset target sebelum
membuatnya kembali. Jangan menyimpan file lain yang ingin dipertahankan di
`dataset\seed_247006111184\`.

## Membaca hasil

- **Speedup** dihitung sebagai `waktu serial / waktu hybrid`.
- **Efisiensi** dihitung sebagai `speedup / jumlah process x 100%`.
- **Throughput** dihitung sebagai `jumlah file / waktu hybrid`.

Speedup atau efisiensi dapat berbeda antar komputer karena dipengaruhi
kecepatan disk, jumlah core CPU, beban sistem, dan overhead pembuatan thread
serta process.

## Struktur file utama

```text
uts\
├── hybrid_file_analyzer.py   # Program utama serial dan hybrid
├── run_experiments.py        # Pengujian beberapa konfigurasi
├── dataset\                  # Dataset yang dibuat program
├── hasil_eksperimen.csv      # Hasil eksperimen
└── grafik*.png               # Grafik hasil eksperimen
```

