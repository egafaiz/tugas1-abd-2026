"""
Unduh data cuaca per jam (ERA5, via Open-Meteo Historical Weather API)
untuk 38 ibu kota provinsi di Indonesia, periode 2020-01-01 s.d. 2024-12-31.

Output: satu file CSV per kota di data/raw/openmeteo/
Jalankan dari root repository:
    python src/download_data.py

Sumber : https://open-meteo.com/en/docs/historical-weather-api
Lisensi: CC BY 4.0 (https://open-meteo.com/en/licence)
Hanya memakai library standar Python, jadi tidak menambah dependency.
"""

import csv
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_URL = "https://archive-api.open-meteo.com/v1/archive"
START_DATE = "2020-01-01"
END_DATE = "2024-12-31"
MODEL = "era5"  # satu model saja agar konsisten sepanjang periode
HOURLY_VARS = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "weather_code",
    "cloud_cover",
    "surface_pressure",
    "wind_speed_10m",
    "wind_direction_10m",
]

OUT_DIR = Path(__file__).resolve().parents[1] / "data" / "raw" / "openmeteo"

# (provinsi, ibu kota, latitude, longitude)
LOCATIONS = [
    ("Aceh", "Banda Aceh", 5.5483, 95.3238),
    ("Sumatera Utara", "Medan", 3.5952, 98.6722),
    ("Sumatera Barat", "Padang", -0.9471, 100.4172),
    ("Riau", "Pekanbaru", 0.5071, 101.4478),
    ("Kepulauan Riau", "Tanjung Pinang", 0.9186, 104.4554),
    ("Jambi", "Jambi", -1.6101, 103.6131),
    ("Bengkulu", "Bengkulu", -3.8004, 102.2655),
    ("Sumatera Selatan", "Palembang", -2.9761, 104.7754),
    ("Kepulauan Bangka Belitung", "Pangkal Pinang", -2.1316, 106.1169),
    ("Lampung", "Bandar Lampung", -5.3971, 105.2668),
    ("DKI Jakarta", "Jakarta", -6.2088, 106.8456),
    ("Banten", "Serang", -6.1104, 106.1640),
    ("Jawa Barat", "Bandung", -6.9175, 107.6191),
    ("Jawa Tengah", "Semarang", -6.9667, 110.4167),
    ("DI Yogyakarta", "Yogyakarta", -7.7956, 110.3695),
    ("Jawa Timur", "Surabaya", -7.2575, 112.7521),
    ("Bali", "Denpasar", -8.6705, 115.2126),
    ("Nusa Tenggara Barat", "Mataram", -8.5833, 116.1167),
    ("Nusa Tenggara Timur", "Kupang", -10.1772, 123.6070),
    ("Kalimantan Barat", "Pontianak", -0.0263, 109.3425),
    ("Kalimantan Tengah", "Palangka Raya", -2.2136, 113.9108),
    ("Kalimantan Selatan", "Banjarbaru", -3.4425, 114.8450),
    ("Kalimantan Timur", "Samarinda", -0.5022, 117.1536),
    ("Kalimantan Utara", "Tanjung Selor", 2.8375, 117.3653),
    ("Sulawesi Utara", "Manado", 1.4748, 124.8421),
    ("Gorontalo", "Gorontalo", 0.5435, 123.0568),
    ("Sulawesi Tengah", "Palu", -0.8917, 119.8707),
    ("Sulawesi Barat", "Mamuju", -2.6748, 118.8885),
    ("Sulawesi Selatan", "Makassar", -5.1477, 119.4327),
    ("Sulawesi Tenggara", "Kendari", -3.9985, 122.5129),
    ("Maluku", "Ambon", -3.6954, 128.1814),
    ("Maluku Utara", "Sofifi", 0.7372, 127.5590),
    ("Papua", "Jayapura", -2.5337, 140.7181),
    ("Papua Barat", "Manokwari", -0.8615, 134.0620),
    ("Papua Barat Daya", "Sorong", -0.8762, 131.2558),
    ("Papua Tengah", "Nabire", -3.3667, 135.4833),
    ("Papua Pegunungan", "Wamena", -4.0956, 138.9453),
    ("Papua Selatan", "Merauke", -8.4932, 140.4018),
]


def slugify(text: str) -> str:
    return text.lower().replace(" ", "_")


def fetch(lat: float, lon: float, max_retries: int = 5) -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "hourly": ",".join(HOURLY_VARS),
        "models": MODEL,
        "timezone": "auto",  # jam lokal (WIB/WITA/WIT)
    }
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=120) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as err:
            if err.code == 429:  # kuota API gratis sedang habis
                wait = 60 * attempt
                print(f"  kena limit (429), tunggu {wait} detik...")
                time.sleep(wait)
            else:
                raise
        except urllib.error.URLError as err:
            wait = 10 * attempt
            print(f"  gagal koneksi ({err.reason}), coba lagi {wait} detik...")
            time.sleep(wait)
    raise RuntimeError("Gagal mengunduh setelah beberapa kali percobaan")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total_rows = 0
    for i, (prov, kota, lat, lon) in enumerate(LOCATIONS, start=1):
        out_file = OUT_DIR / f"{slugify(prov)}.csv"
        if out_file.exists():
            print(f"[{i:02d}/38] {prov} sudah ada, dilewati")
            continue

        print(f"[{i:02d}/38] Mengunduh {prov} ({kota})...")
        data = fetch(lat, lon)
        hourly = data["hourly"]
        tz = data.get("timezone", "")

        header = ["provinsi", "kota", "latitude", "longitude", "timezone", "time"] + HOURLY_VARS
        tmp_file = out_file.with_suffix(".csv.part")
        with open(tmp_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for j, ts in enumerate(hourly["time"]):
                writer.writerow(
                    [prov, kota, lat, lon, tz, ts] + [hourly[v][j] for v in HOURLY_VARS]
                )
        tmp_file.rename(out_file)  # file baru "jadi" setelah lengkap

        n = len(hourly["time"])
        total_rows += n
        print(f"         {n:,} baris -> {out_file.name}")
        time.sleep(15)  # jeda agar tidak melewati batas API gratis per menit

    print(f"Selesai. Baris yang baru diunduh: {total_rows:,}")


if __name__ == "__main__":
    main()
