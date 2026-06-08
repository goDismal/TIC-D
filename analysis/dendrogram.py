"""
dendrogram.py — Generación de dendrograma de similitud curricular.

Flujo:
    1. Lee data/processed/carreras_homologas.csv
    2. Concatena perfil_egreso + perfil_profesional por carrera
    3. Vectoriza con TF-IDF (español, stopwords incluidas)
    4. Calcula distancia coseno entre todos los pares
    5. Clustering jerárquico con método Ward
    6. Guarda dendrograma en outputs/ como PNG y PDF

Uso:
    python analysis/dendrogram.py
    python analysis/dendrogram.py --siglas EPN ESPOL UPS
    python analysis/dendrogram.py --campo perfil_egreso
    python analysis/dendrogram.py --metodo complete

Salida:
    outputs/dendrograma_YYYYMMDD.png
    outputs/dendrograma_YYYYMMDD.pdf
    outputs/dendrograma_YYYYMMDD_metadata.json
"""

import argparse
import json
import os
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── Rutas ──────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent.parent
INPUT_CSV  = BASE_DIR / "data" / "processed" / "carreras_homologas.csv"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── Stopwords español ──────────────────────────────────────────────────────────
STOPWORDS_ES = [
    "de","la","el","en","y","a","los","las","que","se","del","un","una",
    "con","por","para","su","sus","es","son","al","lo","como","más","o",
    "pero","si","le","da","han","hay","ser","estar","tiene","tienen","puede",
    "pueden","así","este","esta","estos","estas","entre","también","todo",
    "todos","toda","todas","sobre","cuando","donde","quien","quienes","cada",
    "mediante","través","hacia","hasta","desde","durante","sin","bajo",
    "según","tanto","cuya","cuyo","cuyos","cuyas","propio","propios",
    "propia","propias","diferentes","diversas","diversos","dicha","dichos",
    "no","ni","me","te","nos","les","muy","bien","mejor","mayor","otro",
    "otros","otra","otras","mismo","misma","mismos","mismas",
]

# ── Paleta de colores por universidad ──────────────────────────────────────────
PALETA = {
    "EPN":   "#1a56db",
    "ESPOL": "#0e9f6e",
    "UPS":   "#e3a008",
    "ESPOCH":"#9061f9",
    "UCE":   "#e02424",
    "UTM":   "#ff5a1f",
    "UG":    "#057a55",
    "USFQ":  "#0694a2",
    "UDLA":  "#c81e1e",
    "UTPL":  "#5521b5",
    "ESPE":  "#1e429f",
    "UCSG":  "#723b13",
    "PUCE":  "#014737",
    "UTN":   "#6b21a8",
}

def get_color(siglas):
    return PALETA.get(siglas, "#4b5563")

# ── CLI ────────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="Dendrograma de similitud curricular")
    p.add_argument("--input",        default=str(INPUT_CSV))
    p.add_argument("--siglas",       nargs="+", default=None)
    p.add_argument("--campo",        default="ambos",
                   choices=["perfil_egreso","perfil_profesional","ambos"])
    p.add_argument("--metodo",       default="ward",
                   choices=["ward","complete","average","single"])
    p.add_argument("--max-features", type=int, default=3000)
    p.add_argument("--dpi",          type=int, default=150)
    return p.parse_args()

# ── Procesamiento ──────────────────────────────────────────────────────────────
def cargar_datos(csv_path, siglas_filtro=None):
    df = pd.read_csv(csv_path)
    df["perfil_egreso"]      = df["perfil_egreso"].fillna("")
    df["perfil_profesional"] = df["perfil_profesional"].fillna("")
    if siglas_filtro:
        df = df[df["siglas"].isin(siglas_filtro)].copy()
        print(f"  Filtro: {siglas_filtro} → {len(df)} carreras")
    return df.reset_index(drop=True)

def construir_corpus(df, campo):
    if campo == "perfil_egreso":
        return df["perfil_egreso"].tolist()
    elif campo == "perfil_profesional":
        return df["perfil_profesional"].tolist()
    return (df["perfil_egreso"] + " " + df["perfil_profesional"]).tolist()

def vectorizar(corpus, max_features):
    vec = TfidfVectorizer(
        max_features=max_features,
        stop_words=STOPWORDS_ES,
        ngram_range=(1, 2),
        min_df=2,
        sublinear_tf=True,
    )
    mat = vec.fit_transform(corpus)
    print(f"  Vocabulario: {len(vec.vocabulary_)} términos")
    print(f"  Matriz: {mat.shape[0]} × {mat.shape[1]}")
    return mat

def calcular_distancia(mat):
    sim = cosine_similarity(mat)
    dist = np.clip(1 - sim, 0, None)
    np.fill_diagonal(dist, 0)
    return dist

# ── Figura ─────────────────────────────────────────────────────────────────────
def generar_dendrograma(df, dist_matrix, metodo, campo, dpi):
    n = len(df)
    Z = linkage(squareform(dist_matrix, checks=False), method=metodo)

    etiquetas = (df["nombre"].str.title() + "\n" + df["siglas"]).tolist()

    fig_h = max(22, n * 0.23)
    fig, ax = plt.subplots(figsize=(18, fig_h))
    fig.patch.set_facecolor("#fafafa")
    ax.set_facecolor("#fafafa")

    dendrogram(
        Z,
        labels=etiquetas,
        orientation="left",
        ax=ax,
        leaf_font_size=7.5,
        color_threshold=0.6 * max(Z[:, 2]),
        above_threshold_color="#9ca3af",
        count_sort="descendent",
    )

    # Colorear etiquetas por universidad
    for tick in ax.get_yticklabels():
        txt = tick.get_text()
        partes = txt.split("\n")
        if len(partes) >= 2:
            tick.set_color(get_color(partes[-1].strip()))

    ax.set_xlabel("Distancia coseno  (1 − similitud TF-IDF)",
                  fontsize=11, labelpad=10, color="#374151")
    ax.set_title(
        f"Similitud curricular entre carreras — Ecuador\n"
        f"TF-IDF · {campo.replace('_',' ')} · Linkage {metodo} · "
        f"{n} carreras · {df['siglas'].nunique()} universidades",
        fontsize=13, fontweight="bold", color="#111827", pad=16,
    )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="x", colors="#6b7280", labelsize=9)
    ax.grid(axis="x", linestyle="--", alpha=0.4, color="#d1d5db")

    # Leyenda
    handles = [
        plt.matplotlib.patches.Patch(
            color=get_color(sig),
            label=f"{sig}  ({(df['siglas']==sig).sum()})"
        )
        for sig in sorted(df["siglas"].unique())
    ]
    leg = ax.legend(handles=handles, title="Universidad", loc="lower right",
                    fontsize=8, title_fontsize=9, framealpha=0.9,
                    edgecolor="#e5e7eb", ncol=2)
    leg.get_title().set_color("#374151")

    plt.tight_layout(pad=1.5)

    fecha    = date.today().isoformat()
    base     = f"dendrograma_{fecha}"
    png_path = OUTPUT_DIR / f"{base}.png"
    pdf_path = OUTPUT_DIR / f"{base}.pdf"

    fig.savefig(png_path, dpi=dpi, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    fig.savefig(pdf_path, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)

    print(f"  PNG: {png_path}")
    print(f"  PDF: {pdf_path}")

    meta = {
        "fecha": fecha, "n_carreras": n,
        "n_universidades": int(df["siglas"].nunique()),
        "campo_usado": campo, "metodo_linkage": metodo,
        "universidades": df["siglas"].value_counts().to_dict(),
        "png": str(png_path), "pdf": str(pdf_path),
    }
    meta_path = OUTPUT_DIR / f"{base}_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"  Metadata: {meta_path}")
    return meta

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    args = parse_args()
    print("=" * 60)
    print("DENDROGRAMA DE SIMILITUD CURRICULAR — TIC-D")
    print("=" * 60)

    print(f"\n[1/4] Cargando {args.input}")
    df = cargar_datos(args.input, args.siglas)
    print(f"  {len(df)} carreras · {df['siglas'].nunique()} universidades")

    print(f"\n[2/4] Corpus ({args.campo})")
    corpus = construir_corpus(df, args.campo)

    print(f"\n[3/4] TF-IDF (max_features={args.max_features})")
    mat = vectorizar(corpus, args.max_features)

    print(f"\n[4/4] Clustering y dendrograma")
    dist = calcular_distancia(mat)
    meta = generar_dendrograma(df, dist, args.metodo, args.campo, args.dpi)

    print("\n" + "=" * 60)
    print(f"  Carreras:      {meta['n_carreras']}")
    print(f"  Universidades: {meta['n_universidades']}")
    print(f"  Campo:         {meta['campo_usado']}")
    print(f"  Método:        {meta['metodo_linkage']}")
    print("=" * 60)

if __name__ == "__main__":
    main()
