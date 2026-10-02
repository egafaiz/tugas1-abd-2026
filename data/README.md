# Data Tugas 1

## Dataset yang Dipilih

| Item | Isi |
|---|---|
| Nama dataset | Data Cuaca Per Jam 38 Ibu Kota Provinsi Indonesia 2020–2024 (reanalisis ERA5 via Open-Meteo Historical Weather API) |
| Sumber | [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api), endpoint `https://archive-api.open-meteo.com/v1/archive`; data asli: [ERA5 hourly data on single levels, ECMWF/Copernicus](https://doi.org/10.24381/cds.adbb2d47) |
| Lisensi/ketentuan pakai | [CC BY 4.0](https://open-meteo.com/en/licence): boleh dibagikan dan diolah dengan atribusi "Weather data by Open-Meteo.com". Sitasi: Zippenfenig, P. (2023). *Open-Meteo.com Weather API*. Zenodo. https://doi.org/10.5281/ZENODO.7970649 dan Hersbach, H. et al. (2023). *ERA5 hourly data on single levels from 1940 to present*. ECMWF. https://doi.org/10.24381/cds.adbb2d47 |
| Ukuran | **1.666.224 baris** (38 lokasi × 1.827 hari × 24 jam), 14 kolom, 38 file CSV berukuran total 172 MB. Memenuhi syarat > 1.000.000 baris. |
| Periode data | 1 Januari 2020 00:00 – 31 Desember 2024 23:00, resolusi per jam, waktu lokal (WIB/WITA/WIT) |
| Unit analisis | Satu observasi cuaca per jam di satu titik ibu kota provinsi (38 provinsi). Grid ERA5 berukuran 0,25° (±25 km). |

### Kolom

| Kolom | Satuan | Keterangan |
|---|---|---|
| `provinsi` | - | Nama provinsi |
| `kota` | - | Ibu kota provinsi (titik koordinat yang diminta) |
| `latitude`, `longitude` | derajat (WGS84) | Koordinat yang diminta |
| `timezone` | - | Zona waktu lokal (`Asia/Jakarta`, `Asia/Makassar`, `Asia/Jayapura`) |
| `time` | ISO 8601 | Jam observasi dalam waktu lokal |
| `temperature_2m` | °C | Suhu udara 2 m di atas tanah |
| `relative_humidity_2m` | % | Kelembapan relatif 2 m |
| `precipitation` | mm | Total presipitasi pada satu jam sebelumnya |
| `weather_code` | kode WMO | Kondisi cuaca (0 = cerah, 61–65 = hujan, 95 = badai petir, dst.) |
| `cloud_cover` | % | Tutupan awan total |
| `surface_pressure` | hPa | Tekanan udara permukaan |
| `wind_speed_10m` | km/jam | Kecepatan angin 10 m |
| `wind_direction_10m` | ° | Arah angin 10 m |

### Kesesuaian dengan Tugas

- **Ukuran:** 1,67 juta baris, melebihi syarat 1 juta baris.
- **Temporal:** deret waktu per jam selama 5 tahun, cukup untuk pola diurnal, musiman (musim hujan/kemarau), dan tren tahunan.
- **Spasial:** 38 provinsi dari Aceh sampai Papua Selatan beserta koordinatnya, cukup untuk peta dan perbandingan antarwilayah.
- **Data quality:** dapat diuji untuk null, duplikasi `(provinsi, time)`, kelengkapan jam, rentang nilai fisik (misalnya kelembapan 0–100%, presipitasi ≥ 0), dan outlier hujan ekstrem.

### Keterbatasan

- Data ini adalah **reanalisis** (model yang diasimilasi dengan observasi), bukan pengukuran langsung stasiun BMKG. Nilainya mewakili rata-rata grid ±25 km sehingga hujan ekstrem lokal cenderung lebih rendah daripada catatan stasiun.
- Satu titik per provinsi mewakili ibu kota, bukan seluruh wilayah provinsi.

## Tempat Mencari Dataset

| Situs | Kegunaan |
|---|---|
| [Satu Data Indonesia](https://data.go.id/) | Portal data terbuka lintas instansi pemerintah Indonesia. |
| [Badan Pusat Statistik](https://www.bps.go.id/) | Statistik sosial, ekonomi, kependudukan, dan data wilayah. |
| [BMKG Data Online](https://dataonline.bmkg.go.id/) | Data cuaca, iklim, gempa bumi, dan observasi meteorologi. |
| [Hugging Face Datasets](https://huggingface.co/datasets) | Dataset publik yang dapat dicari berdasarkan topik, bahasa, atau ukuran. |
| [Kaggle Datasets](https://www.kaggle.com/datasets) | Katalog dataset publik; periksa lisensi dan dokumentasi pembuatnya. |
| [Google Dataset Search](https://datasetsearch.research.google.com/) | Mesin pencari untuk menemukan dataset dari berbagai portal. |

## Cara Memperoleh Data

Data diunduh dengan script `src/download_data.py`. Script ini hanya memakai library standar Python, jadi tidak perlu instalasi tambahan.

1. Dari root repository, jalankan:

   ```bash
   python src/download_data.py
   ```

   Script mengirim 1 request per provinsi (total 38) ke Open-Meteo dengan parameter `models=era5`, `timezone=auto`, dan periode 2020-01-01 s.d. 2024-12-31. Proses ini memakan waktu ±10–15 menit karena ada jeda antar-request.
2. Hasilnya tersimpan sebagai 38 file CSV di `data/raw/openmeteo/<provinsi>.csv` (contoh `jawa_timur.csv`). Total ±1,67 juta baris.
3. Kalau proses terputus atau terkena batas API (HTTP 429), jalankan ulang perintah yang sama. File yang sudah lengkap akan dilewati, dan script menunggu otomatis ketika terkena limit.
4. Catat checksum file setelah unduhan selesai:

   ```bash
   # Linux / macOS / Git Bash
   sha256sum data/raw/openmeteo/*.csv > data/raw/checksums.sha256
   ```

   ```powershell
   # PowerShell
   Get-FileHash data/raw/openmeteo/*.csv -Algorithm SHA256 | Format-Table Hash, Path > data/raw/checksums.txt
   ```

5. `DATA_PATH` di `notebooks/01_data_profiling.ipynb` sudah menunjuk ke pola glob berikut. Semua file dibaca sekaligus:

   ```python
   DATA_PATH = "data/raw/openmeteo/*.csv"

   import polars as pl
   lf = pl.scan_csv(DATA_PATH, try_parse_dates=True)
   ```

   Contoh dengan DuckDB: `SELECT * FROM read_csv_auto('data/raw/openmeteo/*.csv')`.

## Aturan Penyimpanan

- Jangan commit dataset mentah atau hasil olahan berukuran besar ke Git. Pastikan `data/raw/` dan `data/processed/` tercantum di `.gitignore`.
- File pada `data/raw/` adalah data asli dan tidak boleh diubah.
- Simpan hasil transformasi yang dapat direproduksi pada `data/processed/`, sebaiknya dalam format Parquet.
