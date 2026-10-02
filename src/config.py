"""Konfigurasi bersama: path, metadata wilayah, dan aturan kualitas data."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "openmeteo"
RAW_GLOB = str(RAW_DIR / "*.csv")
PROCESSED_DIR = ROOT / "data" / "processed"
CLEAN_PARQUET = PROCESSED_DIR / "cuaca_bersih.parquet"
FIGURES_DIR = ROOT / "output" / "figures"

START = "2020-01-01 00:00"
END = "2024-12-31 23:00"
N_PROVINSI = 38
JAM_PER_PROVINSI = 1827 * 24  # 2020-01-01 s.d. 2024-12-31 (dua tahun kabisat)

# Pengelompokan provinsi ke pulau/kepulauan besar untuk analisis spasial.
PULAU = {
    "Aceh": "Sumatera",
    "Sumatera Utara": "Sumatera",
    "Sumatera Barat": "Sumatera",
    "Riau": "Sumatera",
    "Kepulauan Riau": "Sumatera",
    "Jambi": "Sumatera",
    "Bengkulu": "Sumatera",
    "Sumatera Selatan": "Sumatera",
    "Kepulauan Bangka Belitung": "Sumatera",
    "Lampung": "Sumatera",
    "DKI Jakarta": "Jawa",
    "Banten": "Jawa",
    "Jawa Barat": "Jawa",
    "Jawa Tengah": "Jawa",
    "DI Yogyakarta": "Jawa",
    "Jawa Timur": "Jawa",
    "Bali": "Bali-Nusa Tenggara",
    "Nusa Tenggara Barat": "Bali-Nusa Tenggara",
    "Nusa Tenggara Timur": "Bali-Nusa Tenggara",
    "Kalimantan Barat": "Kalimantan",
    "Kalimantan Tengah": "Kalimantan",
    "Kalimantan Selatan": "Kalimantan",
    "Kalimantan Timur": "Kalimantan",
    "Kalimantan Utara": "Kalimantan",
    "Sulawesi Utara": "Sulawesi",
    "Gorontalo": "Sulawesi",
    "Sulawesi Tengah": "Sulawesi",
    "Sulawesi Barat": "Sulawesi",
    "Sulawesi Selatan": "Sulawesi",
    "Sulawesi Tenggara": "Sulawesi",
    "Maluku": "Maluku",
    "Maluku Utara": "Maluku",
    "Papua": "Papua",
    "Papua Barat": "Papua",
    "Papua Barat Daya": "Papua",
    "Papua Tengah": "Papua",
    "Papua Pegunungan": "Papua",
    "Papua Selatan": "Papua",
}

URUTAN_PULAU = [
    "Sumatera",
    "Jawa",
    "Bali-Nusa Tenggara",
    "Kalimantan",
    "Sulawesi",
    "Maluku",
    "Papua",
]

ZONA_WAKTU = {
    "Asia/Jakarta": "WIB",
    "Asia/Pontianak": "WIB",
    "Asia/Makassar": "WITA",
    "Asia/Jayapura": "WIT",
}

# Kode cuaca WMO yang mungkin muncul (lihat dokumentasi Open-Meteo).
WEATHER_CODES = {
    0: "Cerah",
    1: "Umumnya cerah",
    2: "Berawan sebagian",
    3: "Berawan/mendung",
    45: "Kabut",
    48: "Kabut beku",
    51: "Gerimis ringan",
    53: "Gerimis sedang",
    55: "Gerimis lebat",
    61: "Hujan ringan",
    63: "Hujan sedang",
    65: "Hujan lebat",
    80: "Hujan lokal ringan",
    81: "Hujan lokal sedang",
    82: "Hujan lokal sangat lebat",
    95: "Badai petir",
}

# Rentang nilai yang masuk akal secara fisik untuk wilayah Indonesia.
# Nilai di luar rentang ini dianggap tidak valid (bukan sekadar outlier).
RENTANG_FISIK = {
    "temperature_2m": (5.0, 45.0),  # °C; dataran tinggi Papua bisa < 15 °C
    "relative_humidity_2m": (0, 100),  # %
    "precipitation": (0.0, 200.0),  # mm/jam
    "cloud_cover": (0, 100),  # %
    "surface_pressure": (700.0, 1050.0),  # hPa; stasiun tinggi bertekanan rendah
    "wind_speed_10m": (0.0, 150.0),  # km/jam
    "wind_direction_10m": (0, 360),  # derajat
}

KOLOM_NUMERIK = list(RENTANG_FISIK.keys())
