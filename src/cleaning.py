"""Pipeline cleaning berbasis Polars LazyFrame.

Setiap fungsi menerima dan mengembalikan LazyFrame. Pekerjaan baru dijalankan
saat .collect() atau .sink_parquet() dipanggil, sehingga Polars bisa
mengoptimalkan seluruh rantai transformasi (projection/predicate pushdown).
"""

import polars as pl

from src.config import PULAU, RENTANG_FISIK, WEATHER_CODES, ZONA_WAKTU

SCHEMA_RAW = {
    "provinsi": pl.String,
    "kota": pl.String,
    "latitude": pl.Float64,
    "longitude": pl.Float64,
    "timezone": pl.String,
    "time": pl.String,
    "temperature_2m": pl.Float64,
    "relative_humidity_2m": pl.Float64,
    "precipitation": pl.Float64,
    "weather_code": pl.Float64,
    "cloud_cover": pl.Float64,
    "surface_pressure": pl.Float64,
    "wind_speed_10m": pl.Float64,
    "wind_direction_10m": pl.Float64,
}

KOLOM_INTERPOLASI = [
    "temperature_2m",
    "relative_humidity_2m",
    "cloud_cover",
    "surface_pressure",
    "wind_speed_10m",
]


def load_raw(path: str) -> pl.LazyFrame:
    """Baca semua CSV mentah secara lazy dengan skema eksplisit.

    Kolom numerik dibaca sebagai Float64 agar nilai kosong atau desimal yang tidak
    terduga tidak membuat pembacaan gagal; tipe final ditentukan di
    standardize_types().
    """
    return pl.scan_csv(path, schema=SCHEMA_RAW)


def standardize_types(lf: pl.LazyFrame) -> pl.LazyFrame:
    """Parse waktu, rapikan teks, dan perkecil tipe data numerik."""
    return lf.with_columns(
        pl.col("time").str.to_datetime("%Y-%m-%dT%H:%M", strict=False),
        pl.col("provinsi").str.strip_chars(),
        pl.col("kota").str.strip_chars(),
        pl.col("latitude").cast(pl.Float32),
        pl.col("longitude").cast(pl.Float32),
        pl.col("temperature_2m").cast(pl.Float32),
        pl.col("relative_humidity_2m").cast(pl.Float32),
        pl.col("precipitation").cast(pl.Float32),
        pl.col("weather_code").cast(pl.Int16),
        pl.col("cloud_cover").cast(pl.Float32),
        pl.col("surface_pressure").cast(pl.Float32),
        pl.col("wind_speed_10m").cast(pl.Float32),
        pl.col("wind_direction_10m").cast(pl.Float32),
    )


def drop_duplicates(lf: pl.LazyFrame) -> pl.LazyFrame:
    """Satu provinsi hanya boleh punya satu baris per jam."""
    return lf.unique(subset=["provinsi", "time"], keep="first", maintain_order=True)


def invalidate_out_of_range(lf: pl.LazyFrame) -> pl.LazyFrame:
    """Nilai di luar rentang fisik diubah menjadi null agar ditangani bersama missing value.

    Kode cuaca yang tidak dikenal juga dijadikan null.
    """
    exprs = [
        pl.when(pl.col(c).is_between(lo, hi)).then(pl.col(c)).otherwise(None).alias(c)
        for c, (lo, hi) in RENTANG_FISIK.items()
    ]
    exprs.append(
        pl.when(pl.col("weather_code").is_in(list(WEATHER_CODES)))
        .then(pl.col("weather_code"))
        .otherwise(None)
        .alias("weather_code")
    )
    return lf.with_columns(exprs)


def impute_missing(lf: pl.LazyFrame) -> pl.LazyFrame:
    """Isi missing value per provinsi secara berurutan menurut waktu.

    - Variabel kontinu: interpolasi linear antar-jam (cuaca berubah halus per jam).
    - Presipitasi: tidak diinterpolasi karena hujan bersifat sporadis; diisi 0 dan
      ditandai pada kolom flag_imputasi.
    - Arah angin dan kode cuaca: forward fill lalu backward fill (kategori/sirkular).
    Baris yang diimputasi diberi flag agar bisa dikecualikan bila perlu.
    """
    semua = KOLOM_INTERPOLASI + ["precipitation", "wind_direction_10m", "weather_code"]
    lf = lf.sort("provinsi", "time").with_columns(
        pl.any_horizontal([pl.col(c).is_null() for c in semua]).alias("flag_imputasi")
    )
    return lf.with_columns(
        *[pl.col(c).interpolate().forward_fill().backward_fill().over("provinsi") for c in KOLOM_INTERPOLASI],
        pl.col("precipitation").fill_null(0.0),
        pl.col("wind_direction_10m").forward_fill().backward_fill().over("provinsi"),
        pl.col("weather_code").forward_fill().backward_fill().over("provinsi"),
    )


def flag_outliers(lf: pl.LazyFrame) -> pl.LazyFrame:
    """Tandai outlier statistik tanpa membuangnya.

    - Suhu: robust z-score per provinsi per bulan kalender (median & MAD),
      |z| > 3.5 dianggap outlier. Dihitung per provinsi karena Wamena
      (dataran tinggi) wajar jauh lebih dingin dari Jakarta.
    - Hujan: jam dengan presipitasi di atas persentil 99,9 provinsi tersebut
      ditandai sebagai hujan ekstrem (peristiwa nyata, bukan error).
    - Angin: metode IQR per provinsi (Q3 + 3*IQR).
    """
    bulan = pl.col("time").dt.month()
    med = pl.col("temperature_2m").median().over("provinsi", bulan)
    mad = (pl.col("temperature_2m") - med).abs().median().over("provinsi", bulan)
    z = 0.6745 * (pl.col("temperature_2m") - med) / mad

    q1 = pl.col("wind_speed_10m").quantile(0.25).over("provinsi")
    q3 = pl.col("wind_speed_10m").quantile(0.75).over("provinsi")

    return lf.with_columns(
        (z.abs() > 3.5).fill_null(False).alias("outlier_suhu"),
        (pl.col("precipitation") > pl.col("precipitation").quantile(0.999).over("provinsi")).alias(
            "hujan_ekstrem"
        ),
        (pl.col("wind_speed_10m") > q3 + 3 * (q3 - q1)).alias("outlier_angin"),
    )


def add_features(lf: pl.LazyFrame) -> pl.LazyFrame:
    """Tambahkan kolom turunan untuk analisis temporal dan spasial."""
    bulan = pl.col("time").dt.month()
    return lf.with_columns(
        pl.col("provinsi").replace_strict(PULAU, default="Lainnya").alias("pulau"),
        pl.col("timezone").replace_strict(ZONA_WAKTU, default="Lainnya").alias("zona_waktu"),
        pl.col("time").dt.date().alias("tanggal"),
        pl.col("time").dt.year().cast(pl.Int16).alias("tahun"),
        bulan.cast(pl.Int8).alias("bulan"),
        pl.col("time").dt.hour().cast(pl.Int8).alias("jam"),
        # Pembagian musim umum di Indonesia (monsun).
        pl.when(bulan.is_in([12, 1, 2]))
        .then(pl.lit("DJF (puncak hujan)"))
        .when(bulan.is_in([3, 4, 5]))
        .then(pl.lit("MAM (peralihan I)"))
        .when(bulan.is_in([6, 7, 8]))
        .then(pl.lit("JJA (puncak kemarau)"))
        .otherwise(pl.lit("SON (peralihan II)"))
        .alias("musim"),
        (pl.col("precipitation") >= 0.1).alias("jam_hujan"),
    )


def clean_pipeline(path: str) -> pl.LazyFrame:
    """Rangkaian lengkap: load -> tipe -> deduplikasi -> validasi -> imputasi -> outlier -> fitur."""
    return (
        load_raw(path)
        .pipe(standardize_types)
        .filter(pl.col("time").is_not_null() & pl.col("provinsi").is_not_null())
        .pipe(drop_duplicates)
        .pipe(invalidate_out_of_range)
        .pipe(impute_missing)
        .pipe(flag_outliers)
        .pipe(add_features)
        .sort("provinsi", "time")
    )
