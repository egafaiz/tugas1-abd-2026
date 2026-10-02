# Tugas 1: Eksplorasi dan Analisis Dataset Besar Indonesia

**Pola Cuaca Per Jam di 38 Ibu Kota Provinsi Indonesia (2020–2024)**

| | |
|---|---|
| Nama | Muhammad Ega Faiz Fadlillah |
| NIM | 202310370311047 |
| Mata kuliah | Analisis Big Data 2026, Universitas Muhammadiyah Malang |

Proyek ini menganalisis **1.666.224 baris** data cuaca per jam (suhu, kelembapan, hujan, awan, tekanan,
angin) dari 38 ibu kota provinsi Indonesia selama 5 tahun. Pipeline memakai **Polars** untuk profiling
dan cleaning, **DuckDB** untuk analitik SQL dan `SUMMARIZE`, serta **Plotly** untuk 7 visualisasi interaktif.

## Status Milestone

| Tahap | Target | Bukti |
|---|---|---|
| Milestone 1 | Pertemuan 3 | Dataset 1,67 juta baris; [`data/README.md`](data/README.md); [`src/download_data.py`](src/download_data.py); [`notebooks/01_data_profiling.ipynb`](notebooks/01_data_profiling.ipynb) |
| Milestone 2 | Pertemuan 5 | Cleaning Polars di [`src/cleaning.py`](src/cleaning.py) dan [`notebooks/02_data_cleaning.ipynb`](notebooks/02_data_cleaning.ipynb), termasuk DuckDB `SUMMARIZE` |
| Milestone 3 | Pertemuan 8 | Analisis spasial, musiman, antartahun, dan diurnal; 7 visualisasi Plotly di [`notebooks/03_eda_and_insights.ipynb`](notebooks/03_eda_and_insights.ipynb) |
| Final | Pertemuan 10 | 6 insight analitik (bagian 6 notebook 03), `Dockerfile`, `.dockerignore`, `requirements.txt`, dan README ini |

## Dataset

| Item | Isi |
|---|---|
| Sumber | [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api), model reanalisis ERA5 (ECMWF/Copernicus) |
| Lisensi | CC BY 4.0, atribusi: *Weather data by Open-Meteo.com* |
| Ukuran | 1.666.224 baris × 14 kolom, 38 file CSV (172 MB); setelah cleaning menjadi 1 file Parquet 16 MB (26 kolom) |
| Periode | 1 Jan 2020 – 31 Des 2024, per jam, waktu lokal (WIB/WITA/WIT) |
| Unit analisis | Satu jam observasi di satu ibu kota provinsi |

Dokumentasi lengkap (kolom, satuan, keterbatasan, dan cara unduh) ada di [`data/README.md`](data/README.md).
Data **tidak** di-commit ke Git; unduh ulang dengan `python src/download_data.py`.

## Struktur Repository

```text
.
├── .github/workflows/lint_check.yml   # cek otomatis: compile src/ dan validasi JSON notebook
├── data/
│   ├── README.md                      # dokumentasi dataset dan cara unduh
│   ├── raw/openmeteo/*.csv            # data mentah (diabaikan Git)
│   └── processed/cuaca_bersih.parquet # hasil notebook 02 (diabaikan Git)
├── notebooks/
│   ├── 01_data_profiling.ipynb        # Milestone 1
│   ├── 02_data_cleaning.ipynb         # Milestone 2
│   └── 03_eda_and_insights.ipynb      # Milestone 3 + insight
├── output/figures/*.html              # 7 visualisasi interaktif (dihasilkan notebook 03)
├── src/
│   ├── config.py                      # path, pemetaan provinsi→pulau, aturan rentang fisik
│   ├── download_data.py               # unduh data dari Open-Meteo
│   ├── cleaning.py                    # pipeline cleaning Polars (lazy)
│   └── viz.py                         # tema Plotly dan palet warna
├── .dockerignore
├── Dockerfile
├── requirements.txt
└── README.md
```

## Cara Menjalankan

Prasyarat: Docker dan Git.

### 1. Build image

```bash
docker build -t tugas1-bigdata .
```

### 2. Jalankan container

Perintah mount folder berbeda per terminal:

```bash
# Linux / macOS / Git Bash
docker run --rm -p 8888:8888 -v "$(pwd)":/home/jovyan/work tugas1-bigdata
```

```powershell
# Windows PowerShell
docker run --rm -p 8888:8888 -v "${PWD}:/home/jovyan/work" tugas1-bigdata
```

```bat
:: Windows Command Prompt
docker run --rm -p 8888:8888 -v "%cd%":/home/jovyan/work tugas1-bigdata
```

Buka `http://localhost:8888/lab`.

> **Catatan:** Dockerfile menjalankan JupyterLab tanpa password atau token untuk penggunaan lokal. Jangan
> gunakan konfigurasi ini di server atau jaringan publik.

### 3. Unduh dataset (sekali saja)

Di JupyterLab, buka **File → New → Terminal**, lalu jalankan:

```bash
python src/download_data.py
```

Proses ini memakan waktu sekitar 10–15 menit dan menghasilkan 38 file di `data/raw/openmeteo/`.

### 4. Jalankan notebook secara berurutan

Buka dan jalankan `01` → `02` → `03` di JupyterLab (**Run → Run All Cells**), atau jalankan semuanya
sekaligus dari terminal:

```bash
jupyter nbconvert --to notebook --execute --inplace \
    notebooks/01_data_profiling.ipynb \
    notebooks/02_data_cleaning.ipynb \
    notebooks/03_eda_and_insights.ipynb
```

Notebook 02 menghasilkan `data/processed/cuaca_bersih.parquet` yang dibutuhkan notebook 03. Visualisasi
interaktif tersimpan di `output/figures/` dan bisa dibuka langsung di browser.

## Pembagian Peran Polars dan DuckDB

| Tugas | Alat | Alasan |
|---|---|---|
| Membaca 38 CSV, profiling, validasi | Polars `scan_csv` (lazy) | Query plan dioptimalkan; hanya kolom yang dibutuhkan yang dibaca |
| Pipeline cleaning (tipe, deduplikasi, imputasi, flag outlier, fitur) | Polars expressions + window `over()` | Transformasi baris dan per-grup efisien, mudah diuji per langkah |
| Profiling data bersih | DuckDB `SUMMARIZE` | Statistik semua kolom dalam satu perintah |
| Agregasi analitik (hujan tahunan, musiman, diurnal, anomali) | DuckDB SQL di atas Parquet | SQL ringkas untuk `GROUP BY`/`CTE`, langsung membaca Parquet |
| Pivot, korelasi, anomali dengan window function | Polars | Reshaping dan operasi DataFrame lanjutan |

## Ringkasan Hasil

**Kualitas data:** 0 missing value, 0 duplikat, 0 nilai di luar rentang fisik, dan 38 provinsi × 43.848 jam
tanpa celah. Pipeline tetap disusun defensif dan diuji pada data yang sengaja dirusak. Outlier diberi flag,
tidak dihapus: 345 jam suhu, 1.632 jam hujan ekstrem, dan 1.068 jam angin.

**Insight utama** (detail dan angka pendukung ada di notebook 03 bagian 6):

1. **Ketimpangan hujan 3,5×**: Maluku Utara 4.903 mm/tahun vs NTT 1.407 mm/tahun; sabuk kering di
   NTT–NTB–Jawa Timur–Merauke.
2. **Tiga pola musim**: Bali–Nusa Tenggara menerima 75,7% hujan pada Nov–Mar (monsun tegas), Sumatera,
   Kalimantan, dan Sulawesi relatif merata, sedangkan Maluku memuncak pada bulan Mei.
3. **2023 kering serentak**: 36 dari 38 provinsi di bawah rata-rata, dan hujan Juli–Oktober di Jawa turun
   80% (139 mm vs 712 mm pada 2022), bertepatan dengan El Niño.
4. **Hujan konvektif siang hari**: 51,2% hujan turun pukul 12.00–17.59 waktu lokal; puncak pukul 14–15
   di semua pulau.
5. **Periode hangat berkelanjutan**: seluruh 18 bulan sejak Juli 2023 di atas normal; suhu rata-rata
   2024 mencapai 27,5 °C vs 26,9 °C pada 2022.
6. **Ketinggian menentukan suhu**: korelasi suhu–tekanan r = 0,9, suhu–lintang r = −0,1; Wamena 20,3 °C.

## Aturan Teknis

- Polars dipakai untuk manipulasi data dan DuckDB untuk analitik SQL.
- Dataset > 1 juta baris (1.666.224).
- Data besar tidak di-commit (lihat `.gitignore`); instruksi unduh ada di `data/README.md`.
- Commit dilakukan bertahap per milestone dengan pesan yang jelas.

## Integritas Akademik dan Penggunaan AI

- Dilarang menyalin kode, laporan, atau visualisasi mahasiswa lain maupun repository publik tanpa sitasi dan atribusi yang jelas.
- Dilarang menggunakan jasa joki atau menyerahkan pekerjaan yang tidak dapat dijelaskan sendiri.
- AI boleh digunakan untuk belajar, mencari rujukan, menjelaskan konsep, atau debugging. AI tidak menggantikan tanggung jawab mahasiswa atas kebenaran dan kualitas solusi.
- Mahasiswa wajib dapat menjelaskan setiap bagian kode, menjalankan serta memverifikasi ulang hasilnya, dan memastikan penggunaan Polars serta DuckDB sesuai standar kuliah.
- Setiap penggunaan AI harus dicantumkan pada bagian AI Disclosure Statement di bawah.
- Pelanggaran pertama bernilai 0 untuk tugas terkait; pelanggaran berikutnya dapat berakibat nilai E untuk mata kuliah sesuai ketentuan akademik.

## AI Disclosure Statement

> Alat AI yang digunakan: Claude (Anthropic).
>
> Bagian yang dibantu: pencarian dan pemilihan dataset, script unduh data (`src/download_data.py`),
> pipeline cleaning (`src/cleaning.py`), penyusunan notebook 01–03 beserta visualisasi dan narasi insight,
> serta dokumentasi README.
>
> Verifikasi yang dilakukan: [ISI SENDIRI — misalnya: menjalankan ulang seluruh notebook di Docker,
> mencocokkan angka insight dengan output sel, membaca dokumentasi Polars/DuckDB/Open-Meteo, dan memahami
> setiap cell].

## Sumber dan Atribusi

- Weather data by [Open-Meteo.com](https://open-meteo.com/), CC BY 4.0. Zippenfenig, P. (2023). *Open-Meteo.com Weather API*. Zenodo. https://doi.org/10.5281/ZENODO.7970649
- Hersbach, H. et al. (2023). *ERA5 hourly data on single levels from 1940 to present*. Copernicus Climate Change Service (C3S). https://doi.org/10.24381/cds.adbb2d47
- Iglewicz, B. & Hoaglin, D. (1993). *How to Detect and Handle Outliers*. ASQC (dasar ambang robust z-score 3,5).
