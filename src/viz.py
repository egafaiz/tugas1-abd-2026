"""Tema Plotly bersama dan helper untuk menyimpan grafik interaktif."""

from pathlib import Path

import plotly.graph_objects as go
import plotly.io as pio

from src.config import FIGURES_DIR, URUTAN_PULAU

# Palet kategorikal (urutan tetap, lolos uji buta warna untuk pasangan bersebelahan).
KATEGORI = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]

# Warna mengikuti entitas, bukan urutan tampil: setiap pulau selalu berwarna sama.
WARNA_PULAU = dict(zip(URUTAN_PULAU, KATEGORI))

# Sekuensial satu hue (biru), terang -> gelap, untuk besaran seperti curah hujan.
SEKUENSIAL = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

# Divergen merah (lebih kering/negatif) - abu-abu netral - biru (lebih basah/positif).
DIVERGEN_HUJAN = [[0.0, "#b32f2f"], [0.25, "#e88a89"], [0.5, "#f0efec"], [0.75, "#86b6ef"], [1.0, "#184f95"]]
# Untuk suhu: biru (lebih dingin) - abu-abu - merah (lebih panas).
DIVERGEN_SUHU = [[0.0, "#184f95"], [0.25, "#86b6ef"], [0.5, "#f0efec"], [0.75, "#e88a89"], [1.0, "#b32f2f"]]

TEKS = "#0b0b0b"
TEKS_SEKUNDER = "#52514e"
GRID = "#e6e5e1"
SURFACE = "#fcfcfb"

pio.templates["tugas1"] = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Inter, Segoe UI, Arial, sans-serif", size=13, color=TEKS),
        title=dict(font=dict(size=17), x=0, xanchor="left"),
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        colorway=KATEGORI,
        xaxis=dict(gridcolor=GRID, linecolor=GRID, zeroline=False, tickfont=dict(color=TEKS_SEKUNDER)),
        yaxis=dict(gridcolor=GRID, linecolor=GRID, zeroline=False, tickfont=dict(color=TEKS_SEKUNDER)),
        hoverlabel=dict(bgcolor="white", font=dict(color=TEKS)),
        legend=dict(font=dict(color=TEKS_SEKUNDER)),
        margin=dict(l=60, r=30, t=80, b=50),
    )
)
pio.templates.default = "plotly_white+tugas1"


def simpan(fig: go.Figure, nama: str) -> Path:
    """Simpan grafik sebagai HTML interaktif di output/figures/."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{nama}.html"
    fig.write_html(path, include_plotlyjs="cdn")
    return path
