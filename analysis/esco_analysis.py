"""
esco_analysis.py — Análisis completo del Nivel 3 ESCO.

Genera tres entregables a partir de los vectores ya calculados por esco_mapping.py:

    1. Tabla de habilidades por carrera
       outputs/esco_tabla_habilidades_MODELO_FECHA.csv
       outputs/esco_tabla_habilidades_MODELO_FECHA.png  (visual para tesis)

    2. Heatmap de similitud entre carreras
       outputs/esco_heatmap_MODELO_FECHA.png
       outputs/esco_heatmap_MODELO_FECHA.pdf

    3. Métricas de evaluación
       outputs/esco_metricas_MODELO_FECHA.json
       outputs/esco_metricas_MODELO_FECHA.png  (tabla visual comparativa)

Uso:
    python analysis/esco_analysis.py
    python analysis/esco_analysis.py --modelo bge-m3
    python analysis/esco_analysis.py --modelo multilingual-e5-large
    python analysis/esco_analysis.py --comparar   # compara todos los modelos disponibles
"""

import argparse
import glob
import json
import logging
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage, cophenet
from scipy.spatial.distance import squareform
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_similarity

# ── Rutas ──────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent.parent
PROCESSED  = BASE_DIR / "data" / "processed"
from datetime import date
OUTPUT_DIR = BASE_DIR / "outputs" / date.today().isoformat() / "nivel3"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Paleta universidades ───────────────────────────────────────────────────────
PALETA = {
    "EPN":"#1a56db","ESPOL":"#0e9f6e","UPS":"#e3a008","ESPOCH":"#9061f9",
    "UCE":"#e02424","UTM":"#ff5a1f","UG":"#057a55","USFQ":"#0694a2",
    "UDLA":"#c81e1e","UTPL":"#5521b5","ESPE":"#1e429f","UCSG":"#723b13",
    "PUCE":"#014737","UTN":"#6b21a8",
}
def get_color(sig): return PALETA.get(sig, "#4b5563")

# ── CLI ────────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="Análisis completo Nivel 3 ESCO")
    p.add_argument("--modelo",   default="bge-m3",
                   help="Nombre corto del modelo (default: bge-m3)")
    p.add_argument("--top-k",   type=int, default=10,
                   help="Top-K habilidades para la tabla visual (default: 10)")
    p.add_argument("--metodo",  default="ward",
                   choices=["ward","complete","average","single"])
    p.add_argument("--comparar",action="store_true",
                   help="Comparar todos los modelos disponibles")
    p.add_argument("--dpi",     type=int, default=150)
    return p.parse_args()

# ── Carga de datos ─────────────────────────────────────────────────────────────
def cargar_datos(modelo: str):
    """Carga carreras, top-K skills y vectores para un modelo dado."""
    # Carreras
    df_carreras = pd.read_csv(PROCESSED / "carreras_homologas.csv")
    df_carreras["perfil_egreso"]      = df_carreras["perfil_egreso"].fillna("")
    df_carreras["perfil_profesional"] = df_carreras["perfil_profesional"].fillna("")

    # Top-K skills
    topk_files = sorted(glob.glob(str(PROCESSED / f"esco_top25_{modelo}_*.csv")))
    if not topk_files:
        raise FileNotFoundError(f"No se encontró esco_top25_{modelo}_*.csv en {PROCESSED}")
    df_topk = pd.read_csv(topk_files[-1])
    log.info(f"  Top-K skills: {topk_files[-1]}")

    # Vectores
    vec_files = sorted(glob.glob(str(PROCESSED / f"esco_vectors_{modelo}_*.npy")))
    if not vec_files:
        raise FileNotFoundError(f"No se encontró esco_vectors_{modelo}_*.npy en {PROCESSED}")
    sim_matrix = np.load(vec_files[-1])
    log.info(f"  Vectores: {vec_files[-1]} — shape: {sim_matrix.shape}")

    return df_carreras, df_topk, sim_matrix

def calcular_sim_carreras(sim_matrix: np.ndarray) -> np.ndarray:
    """Calcula matriz de similitud carrera vs carrera (n×n)."""
    sim_cc = cosine_similarity(sim_matrix)
    np.fill_diagonal(sim_cc, 1.0)
    return sim_cc

# ── 1. Tabla de habilidades ────────────────────────────────────────────────────
def generar_tabla_habilidades(
    df_carreras: pd.DataFrame,
    df_topk: pd.DataFrame,
    modelo: str,
    top_k: int,
    dpi: int,
):
    """
    Genera tabla CSV y PNG con las top-K habilidades ESCO por carrera EPN.
    Útil para mostrar qué competencias caracterizan a cada carrera.
    """
    log.info(f"  Generando tabla de habilidades (top-{top_k} por carrera)...")
    fecha = date.today().isoformat()

    # Filtrar top-K y solo las carreras EPN como referencia
    df_epn = df_topk[
        (df_topk["siglas"] == "EPN") & (df_topk["rank"] <= top_k)
    ].copy()

    # Tabla pivot: carreras EPN × habilidades
    pivot = df_epn.pivot_table(
        index='rank',
        columns='nombre',
        values='skill_label',
        aggfunc='first'
    )
    pivot.index = [f'#{int(i)}' for i in pivot.index]

    # Guardar CSV completo (todas las universidades)
    df_all = df_topk[df_topk["rank"] <= top_k].copy()
    csv_path = OUTPUT_DIR / f"esco_tabla_habilidades_{modelo}_{fecha}.csv"
    df_all.to_csv(csv_path, index=False, encoding="utf-8")
    log.info(f"  CSV guardado: {csv_path}")

    # Figura visual — tabla de habilidades EPN
    n_carreras = len(pivot)
    fig_h = max(8, n_carreras * 0.5 + 2)
    fig, ax = plt.subplots(figsize=(22, fig_h))
    ax.axis("off")
    fig.patch.set_facecolor("#fafafa")

    tabla = ax.table(
        cellText=pivot.values,
        rowLabels=pivot.index,
        colLabels=pivot.columns,
        cellLoc="left",
        loc="center",
    )

    tabla.auto_set_font_size(False)
    tabla.set_fontsize(7.5)
    tabla.auto_set_column_width(col=list(range(len(pivot.columns))))

    # Estilo encabezados
    for (row, col), cell in tabla.get_celld().items():
        if row == 0 or col == -1:
            cell.set_facecolor("#1e429f")
            cell.set_text_props(color="white", fontweight="bold")
        elif row % 2 == 0:
            cell.set_facecolor("#f0f4ff")
        else:
            cell.set_facecolor("#ffffff")
        cell.set_edgecolor("#e5e7eb")

    ax.set_title(
        f"Top-{top_k} habilidades ESCO por carrera EPN — Modelo: {modelo}",
        fontsize=13, fontweight="bold", pad=16, color="#111827",
    )

    png_path = OUTPUT_DIR / f"esco_tabla_habilidades_{modelo}_{fecha}.png"
    fig.savefig(png_path, dpi=dpi, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    log.info(f"  PNG guardado: {png_path}")

    return str(csv_path), str(png_path)

# ── 2. Heatmap de similitud ────────────────────────────────────────────────────
def generar_heatmap(
    df_carreras: pd.DataFrame,
    sim_cc: np.ndarray,
    modelo: str,
    metodo: str,
    dpi: int,
):
    """
    Genera heatmap de similitud carrera vs carrera ordenado por clustering jerárquico.
    Las filas/columnas se reordenan según el dendrograma para que clusters queden juntos.
    """
    log.info("  Generando heatmap de similitud...")
    fecha = date.today().isoformat()
    n = len(df_carreras)

    # Reordenar filas/columnas según clustering
    dist = np.clip(1 - sim_cc, 0, None)
    np.fill_diagonal(dist, 0)
    Z = linkage(squareform(dist, checks=False), method=metodo)

    # Obtener orden de hojas del dendrograma
    from scipy.cluster.hierarchy import leaves_list
    orden = leaves_list(Z)

    sim_ordenada    = sim_cc[np.ix_(orden, orden)]
    etiquetas_orden = (
        df_carreras["nombre"].str.title() + "\n" + df_carreras["siglas"]
    ).iloc[orden].tolist()

    # Etiquetas cortas para el heatmap
    etiquetas_cortas = [
        f"{df_carreras['nombre'].iloc[i][:25]}... — {df_carreras['siglas'].iloc[i]}"
        if len(df_carreras['nombre'].iloc[i]) > 25
        else f"{df_carreras['nombre'].iloc[i]} — {df_carreras['siglas'].iloc[i]}"
        for i in orden
    ]

    fig_size = max(20, n * 0.18)
    fig, ax = plt.subplots(figsize=(fig_size, fig_size))
    fig.patch.set_facecolor("#fafafa")

    # Rango dinámico: excluir la diagonal (siempre 1.0) para calcular min/max real
    mask = ~np.eye(sim_ordenada.shape[0], dtype=bool)
    vmin_real = sim_ordenada[mask].min()
    vmax_real = sim_ordenada[mask].max()
    # Centrar el colormap en el punto medio del rango real
    vcenter = (vmin_real + vmax_real) / 2

    from matplotlib.colors import TwoSlopeNorm
    norm = TwoSlopeNorm(vmin=vmin_real, vcenter=vcenter, vmax=vmax_real)

    im = ax.imshow(
        sim_ordenada,
        cmap="RdYlGn",
        norm=norm,
        aspect="auto",
        interpolation="nearest",
    )

    plt.colorbar(im, ax=ax, label="Similitud coseno", shrink=0.6, pad=0.02)

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(etiquetas_cortas, rotation=90, fontsize=5.5, ha="right")
    ax.set_yticklabels(etiquetas_cortas, fontsize=5.5)

    # Colorear etiquetas Y por universidad
    for i, tick in enumerate(ax.get_yticklabels()):
        sig = df_carreras["siglas"].iloc[orden[i]]
        tick.set_color(get_color(sig))
    for i, tick in enumerate(ax.get_xticklabels()):
        sig = df_carreras["siglas"].iloc[orden[i]]
        tick.set_color(get_color(sig))

    ax.set_title(
        f"Matriz de similitud curricular — Nivel 3: Vectores ESCO\n"
        f"Modelo: {modelo} · Ordenado por clustering Ward · "
        f"{n} carreras · {df_carreras['siglas'].nunique()} universidades",
        fontsize=12, fontweight="bold", color="#111827", pad=14,
    )

    plt.tight_layout(pad=1.5)

    base     = f"esco_heatmap_{modelo}_{fecha}"
    png_path = OUTPUT_DIR / f"{base}.png"
    pdf_path = OUTPUT_DIR / f"{base}.pdf"
    fig.savefig(png_path, dpi=dpi, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    fig.savefig(pdf_path, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)

    log.info(f"  PNG: {png_path}")
    log.info(f"  PDF: {pdf_path}")
    return str(png_path), str(pdf_path)

# ── 3. Métricas de evaluación ──────────────────────────────────────────────────
def calcular_metricas(
    df_carreras: pd.DataFrame,
    sim_cc: np.ndarray,
    sim_matrix_raw: np.ndarray,
    modelo: str,
    metodo: str,
) -> dict:
    """
    Calcula métricas cuantitativas para evaluar la calidad del clustering:

    - Cophenetic correlation: qué tan bien el dendrograma preserva las distancias
      originales. Rango [0,1], valores > 0.7 son considerados buenos.

    - Silhouette score: cohesión y separación de los clusters. Rango [-1,1],
      valores > 0.5 indican clusters bien definidos.
      Se evalúa para k=5,7,10,15 clusters.

    - Pureza de clusters por área: qué porcentaje de carreras del mismo nombre
      quedan en el mismo cluster (ground truth = nombre de carrera).
    """
    log.info("  Calculando métricas de evaluación...")

    dist = np.clip(1 - sim_cc, 0, None)
    np.fill_diagonal(dist, 0)
    dist_condensed = squareform(dist, checks=False)
    Z = linkage(dist_condensed, method=metodo)

    # 1. Cophenetic correlation
    cophenetic_corr, _ = cophenet(Z, dist_condensed)
    log.info(f"  Cophenetic correlation: {cophenetic_corr:.4f}")

    # 2. Silhouette score para distintos k
    silhouette_scores = {}
    from scipy.cluster.hierarchy import fcluster
    for k in [5, 7, 10, 15]:
        labels = fcluster(Z, k, criterion="maxclust")
        if len(set(labels)) > 1:
            score = silhouette_score(sim_cc, labels, metric="precomputed"
                                     if False else "cosine")
            silhouette_scores[f"k={k}"] = round(float(score), 4)
            log.info(f"  Silhouette (k={k}): {score:.4f}")

    # 3. Pureza de clusters (ground truth = nombre de carrera normalizado)
    # Usamos k=10 como referencia
    labels_10 = fcluster(Z, 10, criterion="maxclust")
    df_eval = df_carreras[["siglas","nombre"]].copy()
    df_eval["cluster"] = labels_10
    df_eval["nombre_norm"] = df_eval["nombre"].str.lower().str.strip()

    # Para cada cluster, calcular qué % de carreras comparten el nombre más frecuente
    pureza_total = 0
    for cluster_id in df_eval["cluster"].unique():
        grupo = df_eval[df_eval["cluster"] == cluster_id]
        nombre_mayoría = grupo["nombre_norm"].value_counts().iloc[0]
        pureza_total  += nombre_mayoría / len(grupo)
    pureza_promedio = pureza_total / df_eval["cluster"].nunique()
    log.info(f"  Pureza promedio de clusters (k=10): {pureza_promedio:.4f}")

    metricas = {
        "modelo":              modelo,
        "metodo_linkage":      metodo,
        "n_carreras":          len(df_carreras),
        "cophenetic_corr":     round(float(cophenetic_corr), 4),
        "silhouette_scores":   silhouette_scores,
        "pureza_clusters_k10": round(float(pureza_promedio), 4),
        "interpretacion": {
            "cophenetic": (
                "Excelente (>0.8)" if cophenetic_corr > 0.8 else
                "Bueno (0.7-0.8)"  if cophenetic_corr > 0.7 else
                "Aceptable (0.6-0.7)" if cophenetic_corr > 0.6 else
                "Débil (<0.6)"
            ),
            "pureza": (
                "Alta (>0.8)"     if pureza_promedio > 0.8 else
                "Media (0.6-0.8)" if pureza_promedio > 0.6 else
                "Baja (<0.6)"
            ),
        }
    }
    return metricas

def guardar_metricas(metricas: dict, modelo: str, dpi: int):
    """Guarda métricas como JSON y genera tabla visual PNG."""
    fecha    = date.today().isoformat()
    json_path = OUTPUT_DIR / f"esco_metricas_{modelo}_{fecha}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metricas, f, ensure_ascii=False, indent=2)
    log.info(f"  JSON: {json_path}")

    # Tabla visual
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis("off")
    fig.patch.set_facecolor("#fafafa")

    datos = [
        ["Modelo",                  metricas["modelo"]],
        ["Método linkage",          metricas["metodo_linkage"]],
        ["Carreras analizadas",     str(metricas["n_carreras"])],
        ["Cophenetic correlation",  f"{metricas['cophenetic_corr']:.4f}  →  {metricas['interpretacion']['cophenetic']}"],
        ["Silhouette k=5",          str(metricas["silhouette_scores"].get("k=5","N/A"))],
        ["Silhouette k=7",          str(metricas["silhouette_scores"].get("k=7","N/A"))],
        ["Silhouette k=10",         str(metricas["silhouette_scores"].get("k=10","N/A"))],
        ["Silhouette k=15",         str(metricas["silhouette_scores"].get("k=15","N/A"))],
        ["Pureza clusters (k=10)",  f"{metricas['pureza_clusters_k10']:.4f}  →  {metricas['interpretacion']['pureza']}"],
    ]

    tabla = ax.table(
        cellText=datos,
        colLabels=["Métrica", "Valor"],
        cellLoc="left",
        loc="center",
        colWidths=[0.4, 0.6],
    )
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(10)

    for (row, col), cell in tabla.get_celld().items():
        if row == 0:
            cell.set_facecolor("#1e429f")
            cell.set_text_props(color="white", fontweight="bold")
        elif row % 2 == 0:
            cell.set_facecolor("#f0f4ff")
        else:
            cell.set_facecolor("#ffffff")
        cell.set_edgecolor("#e5e7eb")
        cell.set_height(0.1)

    ax.set_title(
        f"Métricas de evaluación — Nivel 3 ESCO · Modelo: {modelo}",
        fontsize=12, fontweight="bold", pad=16, color="#111827",
    )

    png_path = OUTPUT_DIR / f"esco_metricas_{modelo}_{fecha}.png"
    fig.savefig(png_path, dpi=dpi, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    log.info(f"  PNG: {png_path}")
    return str(json_path), str(png_path)

# ── Comparación de modelos ─────────────────────────────────────────────────────
def comparar_modelos(metodo: str, dpi: int):
    """Genera tabla comparativa de métricas para todos los modelos disponibles."""
    fecha = date.today().isoformat()
    modelos_disponibles = []

    # Detectar modelos disponibles
    for f in glob.glob(str(PROCESSED / "esco_vectors_*_*.npy")):
        nombre = Path(f).stem.replace("esco_vectors_","").rsplit("_",1)[0]
        if nombre not in modelos_disponibles:
            modelos_disponibles.append(nombre)

    if not modelos_disponibles:
        log.error("No se encontraron vectores en data/processed/")
        return

    log.info(f"  Modelos encontrados: {modelos_disponibles}")

    # Calcular métricas de TF-IDF si existe
    resultados = []
    for modelo in modelos_disponibles:
        try:
            df_carreras, df_topk, sim_matrix = cargar_datos(modelo)
            sim_cc = calcular_sim_carreras(sim_matrix)
            m = calcular_metricas(df_carreras, sim_cc, sim_matrix, modelo, metodo)
            resultados.append(m)
        except Exception as e:
            log.warning(f"  Error procesando {modelo}: {e}")

    if not resultados:
        log.error("No se pudieron calcular métricas para ningún modelo")
        return

    # Tabla comparativa
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.axis("off")
    fig.patch.set_facecolor("#fafafa")

    headers = ["Modelo","Cophenetic","Silhouette k=5","Silhouette k=10","Pureza k=10","Interpretación"]
    datos_tabla = []
    for m in resultados:
        datos_tabla.append([
            m["modelo"],
            f"{m['cophenetic_corr']:.4f}",
            str(m["silhouette_scores"].get("k=5","N/A")),
            str(m["silhouette_scores"].get("k=10","N/A")),
            f"{m['pureza_clusters_k10']:.4f}",
            m["interpretacion"]["cophenetic"],
        ])

    tabla = ax.table(
        cellText=datos_tabla,
        colLabels=headers,
        cellLoc="center",
        loc="center",
    )
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(9)
    tabla.auto_set_column_width(col=list(range(len(headers))))

    for (row, col), cell in tabla.get_celld().items():
        if row == 0:
            cell.set_facecolor("#1e429f")
            cell.set_text_props(color="white", fontweight="bold")
        elif row % 2 == 0:
            cell.set_facecolor("#f0f4ff")
        else:
            cell.set_facecolor("#ffffff")
        cell.set_edgecolor("#e5e7eb")
        cell.set_height(0.12)

    ax.set_title(
        f"Comparación de modelos — Métricas Nivel 3 ESCO",
        fontsize=13, fontweight="bold", pad=16, color="#111827",
    )

    png_path = OUTPUT_DIR / f"esco_comparacion_modelos_{fecha}.png"
    fig.savefig(png_path, dpi=dpi, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    log.info(f"  Comparación guardada: {png_path}")

    # JSON con todos los resultados
    json_path = OUTPUT_DIR / f"esco_comparacion_modelos_{fecha}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    log.info(f"  JSON: {json_path}")

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    args  = parse_args()
    fecha = date.today().isoformat()

    log.info("=" * 60)
    log.info("ANÁLISIS NIVEL 3 ESCO — TIC-D")
    log.info("=" * 60)

    if args.comparar:
        log.info("\n[MODO COMPARACIÓN] Procesando todos los modelos disponibles")
        comparar_modelos(args.metodo, args.dpi)
        return

    log.info(f"\n[0] Cargando datos para modelo: {args.modelo}")
    df_carreras, df_topk, sim_matrix = cargar_datos(args.modelo)
    sim_cc = calcular_sim_carreras(sim_matrix)
    log.info(f"  Carreras: {len(df_carreras)} | Sim matrix: {sim_cc.shape}")

    log.info(f"\n[1/3] Tabla de habilidades (top-{args.top_k} por carrera EPN)")
    csv_tabla, png_tabla = generar_tabla_habilidades(
        df_carreras, df_topk, args.modelo, args.top_k, args.dpi)

    log.info(f"\n[2/3] Heatmap de similitud")
    png_heat, pdf_heat = generar_heatmap(
        df_carreras, sim_cc, args.modelo, args.metodo, args.dpi)

    log.info(f"\n[3/3] Métricas de evaluación")
    metricas = calcular_metricas(
        df_carreras, sim_cc, sim_matrix, args.modelo, args.metodo)
    json_met, png_met = guardar_metricas(metricas, args.modelo, args.dpi)

    log.info("\n" + "=" * 60)
    log.info("COMPLETADO — Archivos generados:")
    log.info(f"  Tabla CSV:    {csv_tabla}")
    log.info(f"  Tabla PNG:    {png_tabla}")
    log.info(f"  Heatmap PNG:  {png_heat}")
    log.info(f"  Heatmap PDF:  {pdf_heat}")
    log.info(f"  Métricas JSON:{json_met}")
    log.info(f"  Métricas PNG: {png_met}")
    log.info("=" * 60)

    log.info(f"\nResumen de métricas ({args.modelo}):")
    log.info(f"  Cophenetic:  {metricas['cophenetic_corr']:.4f}  "
             f"→  {metricas['interpretacion']['cophenetic']}")
    log.info(f"  Pureza k=10: {metricas['pureza_clusters_k10']:.4f}  "
             f"→  {metricas['interpretacion']['pureza']}")

if __name__ == "__main__":
    main()
