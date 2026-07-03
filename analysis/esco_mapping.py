"""
esco_mapping.py — Nivel 3: Representación de carreras como vectores de habilidades ESCO.

Pipeline:
    1. Carga carreras desde data/processed/carreras_homologas.csv
    2. Carga habilidades ESCO desde data/raw/skills_es.csv
    3. Genera embeddings con sentence-transformers (GPU si disponible)
    4. Calcula similitud coseno carrera↔habilidad → top-K habilidades por carrera
    5. Construye vector de habilidades por carrera
    6. Guarda resultados y dendrograma

Uso:
    python analysis/esco_mapping.py
    python analysis/esco_mapping.py --model BAAI/bge-m3
    python analysis/esco_mapping.py --model intfloat/multilingual-e5-large
    python analysis/esco_mapping.py --top-k 20 --reuse-level transversal cross-sector
    python analysis/esco_mapping.py --dry-run
"""

import argparse
import json
import logging
import sys
import time
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform

# ── Rutas ──────────────────────────────────────────────────────────────────────
BASE_DIR     = Path(__file__).parent.parent
CARRERAS_CSV = BASE_DIR / "data" / "processed" / "carreras_homologas.csv"
ESCO_CSV     = BASE_DIR / "data" / "raw" / "skills_es.csv"
PROCESSED    = BASE_DIR / "data" / "processed"
from datetime import date
OUTPUT_DIR = BASE_DIR / "outputs" / date.today().isoformat() / "nivel3"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED.mkdir(exist_ok=True)

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Paleta de colores ──────────────────────────────────────────────────────────
PALETA = {
    "EPN":"#1a56db","ESPOL":"#0e9f6e","UPS":"#e3a008","ESPOCH":"#9061f9",
    "UCE":"#e02424","UTM":"#ff5a1f","UG":"#057a55","USFQ":"#0694a2",
    "UDLA":"#c81e1e","UTPL":"#5521b5","ESPE":"#1e429f","UCSG":"#723b13",
    "PUCE":"#014737","UTN":"#6b21a8",
}
def get_color(sig): return PALETA.get(sig, "#4b5563")

# ── CLI ────────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="Mapeo ESCO de carreras universitarias")
    p.add_argument("--carreras",    default=str(CARRERAS_CSV))
    p.add_argument("--esco",        default=str(ESCO_CSV))
    p.add_argument("--model",       default="BAAI/bge-m3",
                   help="Modelo sentence-transformers (default: BAAI/bge-m3)")
    p.add_argument("--top-k",       type=int, default=25,
                   help="Top-K habilidades ESCO por carrera (default: 25)")
    p.add_argument("--reuse-level", nargs="+",
                   default=["transversal","cross-sector"],
                   choices=["transversal","cross-sector","sector-specific","occupation-specific"])
    p.add_argument("--batch-size",  type=int, default=64)
    p.add_argument("--metodo",      default="ward",
                   choices=["ward","complete","average","single"])
    p.add_argument("--dpi",         type=int, default=150)
    p.add_argument("--dry-run",     action="store_true")
    return p.parse_args()

# ── Carga ──────────────────────────────────────────────────────────────────────
def cargar_carreras(path):
    df = pd.read_csv(path)
    df["perfil_egreso"]      = df["perfil_egreso"].fillna("")
    df["perfil_profesional"] = df["perfil_profesional"].fillna("")
    df["texto"] = df["perfil_egreso"] + " " + df["perfil_profesional"]
    log.info(f"  Carreras: {len(df)} de {df['siglas'].nunique()} universidades")
    return df.reset_index(drop=True)

def cargar_esco(path, reuse_levels):
    df = pd.read_csv(path)
    df = df[df["reuseLevel"].isin(reuse_levels)].copy()
    df["texto_esco"] = df["preferredLabel"] + ". " + df["description"].fillna("")
    df = df[["conceptUri","preferredLabel","skillType","reuseLevel","texto_esco"]]
    df = df.reset_index(drop=True)
    log.info(f"  Habilidades ESCO: {len(df)} (niveles: {reuse_levels})")
    return df

# ── Embeddings ─────────────────────────────────────────────────────────────────
def cargar_modelo(model_name):
    try:
        from sentence_transformers import SentenceTransformer
        import torch
    except ImportError:
        log.error("Instala: pip install sentence-transformers torch")
        sys.exit(1)

    device = "cuda" if __import__("torch").cuda.is_available() else "cpu"
    log.info(f"  Dispositivo: {device.upper()}")
    if device == "cuda":
        import torch
        log.info(f"  GPU: {torch.cuda.get_device_name(0)}")

    log.info(f"  Modelo: {model_name}")
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(model_name, device=device)

def generar_embeddings(model, textos, batch_size, desc=""):
    log.info(f"  Generando {len(textos)} embeddings ({desc})...")
    t0 = time.time()
    emb = model.encode(
        textos,
        batch_size=batch_size,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    log.info(f"  Listo en {time.time()-t0:.1f}s — shape: {emb.shape}")
    return emb

# ── Mapeo carrera → habilidades ESCO ──────────────────────────────────────────
def mapear_habilidades(emb_carreras, emb_esco, df_carreras, df_esco, top_k):
    log.info(f"  Calculando similitud {len(df_carreras)}×{len(df_esco)}...")
    t0 = time.time()
    # Embeddings normalizados → producto punto = similitud coseno
    sim_matrix = np.dot(emb_carreras, emb_esco.T)
    log.info(f"  Listo en {time.time()-t0:.1f}s — shape: {sim_matrix.shape}")

    records = []
    for i, row in df_carreras.iterrows():
        scores  = sim_matrix[i]
        top_idx = np.argsort(scores)[::-1][:top_k]
        for rank, idx in enumerate(top_idx, 1):
            records.append({
                "siglas":      row["siglas"],
                "universidad": row["universidad"],
                "nombre":      row["nombre"],
                "rank":        rank,
                "skill_label": df_esco.loc[idx, "preferredLabel"],
                "skill_type":  df_esco.loc[idx, "skillType"],
                "reuse_level": df_esco.loc[idx, "reuseLevel"],
                "score":       round(float(scores[idx]), 4),
                "skill_uri":   df_esco.loc[idx, "conceptUri"],
            })

    return pd.DataFrame(records), sim_matrix

# ── Dendrograma ────────────────────────────────────────────────────────────────
def generar_dendrograma(df_carreras, sim_matrix, model_name, metodo, reuse_levels, top_k, dpi):
    n    = len(df_carreras)
    # sim_matrix es (n_carreras × n_esco) — calcular similitud carrera vs carrera
    from sklearn.metrics.pairwise import cosine_similarity
    sim_carreras = cosine_similarity(sim_matrix)  # (163 × 163)
    dist = np.clip(1 - sim_carreras, 0, None)
    np.fill_diagonal(dist, 0)
    Z = linkage(squareform(dist, checks=False), method=metodo)

    etiquetas = (df_carreras["nombre"].str.title() + "\n" + df_carreras["siglas"]).tolist()

    fig_h = max(22, n * 0.23)
    fig, ax = plt.subplots(figsize=(18, fig_h))
    fig.patch.set_facecolor("#fafafa")
    ax.set_facecolor("#fafafa")

    dendrogram(Z, labels=etiquetas, orientation="left", ax=ax,
               leaf_font_size=7.5, color_threshold=0.6*max(Z[:,2]),
               above_threshold_color="#9ca3af", count_sort="descendent")

    for tick in ax.get_yticklabels():
        partes = tick.get_text().split("\n")
        if len(partes) >= 2:
            tick.set_color(get_color(partes[-1].strip()))

    model_short = model_name.split("/")[-1]
    ax.set_xlabel("Distancia coseno sobre vectores de habilidades ESCO",
                  fontsize=11, labelpad=10, color="#374151")
    ax.set_title(
        f"Similitud curricular — Nivel 3: Vectores ESCO\n"
        f"Modelo: {model_short} · Niveles: {'+'.join(reuse_levels)} · "
        f"Top-{top_k} skills · Linkage: {metodo} · "
        f"{n} carreras · {df_carreras['siglas'].nunique()} universidades",
        fontsize=12, fontweight="bold", color="#111827", pad=16,
    )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="x", colors="#6b7280", labelsize=9)
    ax.grid(axis="x", linestyle="--", alpha=0.4, color="#d1d5db")

    handles = [
        plt.matplotlib.patches.Patch(color=get_color(s),
            label=f"{s}  ({(df_carreras['siglas']==s).sum()})")
        for s in sorted(df_carreras["siglas"].unique())
    ]
    leg = ax.legend(handles=handles, title="Universidad", loc="lower right",
                    fontsize=8, title_fontsize=9, framealpha=0.9,
                    edgecolor="#e5e7eb", ncol=2)
    leg.get_title().set_color("#374151")
    plt.tight_layout(pad=1.5)

    fecha    = date.today().isoformat()
    base     = f"dendrograma_esco_{model_short}_{fecha}"
    png_path = OUTPUT_DIR / f"{base}.png"
    pdf_path = OUTPUT_DIR / f"{base}.pdf"
    fig.savefig(png_path, dpi=dpi, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(pdf_path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    log.info(f"  PNG: {png_path}")
    log.info(f"  PDF: {pdf_path}")
    return str(png_path), str(pdf_path)

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    args  = parse_args()
    fecha = date.today().isoformat()

    log.info("=" * 60)
    log.info("NIVEL 3: MAPEO ESCO — TIC-D")
    log.info("=" * 60)

    log.info("\n[1/6] Cargando datos")
    df_carreras = cargar_carreras(args.carreras)
    df_esco     = cargar_esco(args.esco, args.reuse_level)

    if args.dry_run:
        log.info("\n[DRY-RUN] Configuración verificada:")
        log.info(f"  Modelo:           {args.model}")
        log.info(f"  Carreras:         {len(df_carreras)}")
        log.info(f"  Habilidades ESCO: {len(df_esco)}")
        log.info(f"  Top-K:            {args.top_k}")
        log.info(f"  Reuse levels:     {args.reuse_level}")
        log.info(f"  Batch size:       {args.batch_size}")
        return

    log.info("\n[2/6] Cargando modelo")
    model = cargar_modelo(args.model)

    log.info("\n[3/6] Embeddings ESCO")
    emb_esco = generar_embeddings(model, df_esco["texto_esco"].tolist(),
                                  args.batch_size, "habilidades ESCO")

    log.info("\n[4/6] Embeddings carreras")
    emb_carreras = generar_embeddings(model, df_carreras["texto"].tolist(),
                                      args.batch_size, "carreras")

    log.info("\n[5/6] Mapeo carrera → ESCO")
    df_topk, sim_matrix = mapear_habilidades(
        emb_carreras, emb_esco, df_carreras, df_esco, args.top_k)

    log.info("\n[6/6] Guardando resultados")
    model_short = args.model.split("/")[-1]

    topk_path = PROCESSED / f"esco_top{args.top_k}_{model_short}_{fecha}.csv"
    df_topk.to_csv(topk_path, index=False, encoding="utf-8")
    log.info(f"  Top-{args.top_k} skills: {topk_path}")

    vec_path = PROCESSED / f"esco_vectors_{model_short}_{fecha}.npy"
    np.save(vec_path, sim_matrix)
    log.info(f"  Vectores: {vec_path}")

    meta = {
        "fecha": fecha, "modelo": args.model,
        "n_carreras": len(df_carreras), "n_habilidades": len(df_esco),
        "reuse_levels": args.reuse_level, "top_k": args.top_k,
        "habilidades": df_esco[["conceptUri","preferredLabel","skillType","reuseLevel"]]
                           .to_dict(orient="records"),
    }
    meta_path = PROCESSED / f"esco_meta_{model_short}_{fecha}.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    log.info(f"  Metadatos: {meta_path}")

    png, pdf = generar_dendrograma(
        df_carreras, sim_matrix, args.model,
        args.metodo, args.reuse_level, args.top_k, args.dpi)

    log.info("\n" + "=" * 60)
    log.info("COMPLETADO")
    log.info(f"  Carreras:     {len(df_carreras)}")
    log.info(f"  Skills ESCO:  {len(df_esco)}")
    log.info(f"  Modelo:       {args.model}")
    log.info(f"  PNG:          {png}")
    log.info("=" * 60)

if __name__ == "__main__":
    main()
