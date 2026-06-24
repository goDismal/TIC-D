"""
pipeline.py — Pipeline principal de recolección de datos de carreras universitarias.

Uso:
    python pipeline.py [--grupo 2] [--siglas UCUENCA UDA] [--dry-run]

Argumentos opcionales:
    --grupo     Número de grupo a procesar (default: 2)
    --siglas    Filtrar por una o más siglas de universidad
    --dry-run   Mostrar qué se procesaría sin hacer requests ni llamadas a API

El script:
  1. Lee la configuración de scrapers/config.py
  2. Para cada universidad y carrera, ejecuta el pipeline de scraping
  3. Guarda resultados incrementalmente en data/carreras_grupo{N}.csv
  4. Guarda un log de ejecución en logs/pipeline_{fecha}.log
  5. Al finalizar imprime un resumen (OK / ERROR / WARN)

Reproducibilidad:
  - Cada fila del CSV incluye: url, metodo_recoleccion, fecha_recoleccion, status
  - El log registra versión del script, timestamp de inicio/fin y conteos
  - Si el CSV ya existe, el script detecta carreras ya procesadas y las omite
    (modo "reanudación") — útil si se interrumpe a mitad
"""

import argparse
import csv
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# ── Rutas ──────────────────────────────────────────────────────────────────────
BASE_DIR  = Path(__file__).parent
from datetime import date
_HOY      = date.today().isoformat()
DATA_DIR  = BASE_DIR / "data"
LOG_DIR   = BASE_DIR / "logs" / _HOY
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ── Logging dual: consola + archivo ───────────────────────────────────────────
def setup_logging(grupo: int) -> logging.Logger:
    log_file = LOG_DIR / f"pipeline_grupo{grupo}_{datetime.now():%Y%m%d_%H%M%S}.log"
    logger = logging.getLogger("pipeline")
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", "%H:%M:%S")

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

# ── CSV helpers ────────────────────────────────────────────────────────────────
COLUMNAS_CSV = [
    "universidad", "siglas", "nombre", "epn_homologa",
    "url", "metodo_recoleccion", "fecha_recoleccion",
    "descripcion", "perfil_ingreso", "perfil_egreso", "perfil_profesional",
    "status",
]

def load_processed(csv_path: Path) -> set[tuple[str, str]]:
    """Retorna el conjunto de (siglas, nombre) ya presentes en el CSV."""
    if not csv_path.exists():
        return set()
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {(r["siglas"], r["nombre"]) for r in reader}

def append_record(csv_path: Path, record: dict) -> None:
    """Añade una fila al CSV; crea el encabezado si el archivo no existe."""
    write_header = not csv_path.exists()
    with open(csv_path, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNAS_CSV, extrasaction="ignore")
        if write_header:
            writer.writeheader()
        writer.writerow(record)

# ── CLI ────────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="Pipeline de scraping de carreras universitarias")
    p.add_argument("--grupo",   type=int, default=2,    help="Grupo a procesar (default: 2)")
    p.add_argument("--siglas",  nargs="+", default=None, help="Filtrar universidades por siglas")
    p.add_argument("--dry-run", action="store_true",    help="Simular sin hacer requests")
    return p.parse_args()

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    args = parse_args()
    log  = setup_logging(args.grupo)

    # Importar configuración y scraper
    sys.path.insert(0, str(BASE_DIR / "scrapers"))
    from config import GRUPO2
    from scraper_base import CarreraScraper

    # Seleccionar grupo
    grupos = {2: GRUPO2}
    if args.grupo not in grupos:
        log.error(f"Grupo {args.grupo} no definido. Grupos disponibles: {list(grupos.keys())}")
        sys.exit(1)

    universidades = grupos[args.grupo]

    # Filtrar por siglas si se especificó
    if args.siglas:
        universidades = [u for u in universidades if u["siglas"] in args.siglas]
        log.info(f"Filtro aplicado: {args.siglas} → {len(universidades)} universidades")

    csv_path = DATA_DIR / f"carreras_grupo{args.grupo}.csv"
    processed = load_processed(csv_path)
    log.info(f"CSV destino: {csv_path}")
    log.info(f"Registros ya procesados: {len(processed)}")

    scraper = CarreraScraper()

    # Contadores
    total = sum(len(u["carreras"]) for u in universidades)
    cnt   = {"ok": 0, "error": 0, "warn": 0, "skip": 0}
    t0    = datetime.now()

    log.info(f"{'='*60}")
    log.info(f"INICIO — Grupo {args.grupo} | {len(universidades)} universidades | {total} carreras")
    log.info(f"{'='*60}")

    for uni in universidades:
        log.info(f"\n▶ {uni['siglas']} — {uni['nombre']}")

        for c in uni["carreras"]:
            key = (uni["siglas"], c["nombre"])

            # Reanudación: omitir si ya está en el CSV
            if key in processed:
                log.info(f"  ↷ {c['nombre']} (ya procesado, omitiendo)")
                cnt["skip"] += 1
                continue

            if args.dry_run:
                log.info(f"  [DRY-RUN] {c['nombre']} → {c['url']}")
                cnt["ok"] += 1
                continue

            record = scraper.scrape_carrera(
                universidad  = uni["nombre"],
                siglas       = uni["siglas"],
                nombre       = c["nombre"],
                epn_homologa = c["epn_homologa"],
                url          = c["url"],
                metodo       = c.get("metodo", "html"),
            )

            append_record(csv_path, record)

            status = record.get("status", "OK")
            if "ERROR" in status:
                cnt["error"] += 1
                log.warning(f"  ✗ {c['nombre']} → {status}")
            elif "WARN" in status:
                cnt["warn"] += 1
                log.warning(f"  ⚠ {c['nombre']} → {status}")
            else:
                cnt["ok"] += 1
                log.info(f"  ✓ {c['nombre']}")

    elapsed = (datetime.now() - t0).seconds
    log.info(f"\n{'='*60}")
    log.info(f"FIN — {elapsed}s | ✓ {cnt['ok']} OK | ⚠ {cnt['warn']} WARN | ✗ {cnt['error']} ERROR | ↷ {cnt['skip']} omitidos")
    log.info(f"CSV guardado en: {csv_path}")
    log.info(f"{'='*60}")

    # Guardar resumen JSON (útil para el repositorio de tesis)
    resumen = {
        "grupo": args.grupo,
        "fecha": datetime.now().isoformat(),
        "universidades": len(universidades),
        "carreras_total": total,
        "resultados": cnt,
        "csv": str(csv_path),
    }
    resumen_path = LOG_DIR / f"resumen_grupo{args.grupo}_{datetime.now():%Y%m%d}.json"
    with open(resumen_path, "w", encoding="utf-8") as f:
        json.dump(resumen, f, ensure_ascii=False, indent=2)
    log.info(f"Resumen guardado en: {resumen_path}")

if __name__ == "__main__":
    main()
