# TIC-D

Repositorio de tesis de grado — Análisis de similitud curricular entre carreras de la Escuela Politécnica Nacional (EPN) y universidades de países miembros y en adhesión a la OCDE, mediante técnicas de NLP y clustering jerárquico.

## Objetivo

Construir un pipeline completo que permita:

1. **Recolectar** perfiles académicos de carreras universitarias (descripción, perfil de ingreso, perfil de egreso, perfil profesional)
2. **Representar** esos perfiles como vectores usando TF-IDF y embeddings multilingües (BETO, Jina, E5)
3. **Medir similitud** entre todas las carreras mediante matrices de distancia coseno
4. **Visualizar** la estructura de similitud mediante dendogramas de clustering jerárquico
5. **Evaluar** qué modelo de embedding produce agrupaciones más coherentes

## Alcance geográfico

| Etapa | País              | Tipo OCDE        |
| ----- | ----------------- | ---------------- |
| 1     | 🇪🇨 Ecuador        | Referencia (EPN) |
| 2     | 🇺🇸 Estados Unidos | Miembro pleno    |
| 2     | 🇲🇽 México         | Miembro pleno    |
| 2     | 🇨🇱 Chile          | Miembro pleno    |
| 2     | 🇨🇴 Colombia       | Miembro pleno    |
| 2     | 🇨🇷 Costa Rica     | Miembro pleno    |
| 2     | 🇦🇷 Argentina      | En adhesión      |
| 2     | 🇧🇷 Brasil         | En adhesión      |
| 2     | 🇵🇪 Perú           | En adhesión      |

## Estructura del repositorio

```
TIC-D/
├── data/
│   ├── raw/                  # Datos fuente sin procesar
│   │   ├── carreras_epn.csv          # Carreras de la EPN (scraper original)
│   │   └── perfiles_egreso.csv       # Primeros perfiles extraídos
│   ├── processed/            # Datos procesados y consolidados
│   │   ├── carreras_homologas.csv    # Dataset maestro Ecuador (en construcción)
│   │   └── grupo3_para_completar.csv # Universidades pequeñas (llenado manual)
│   └── final/                # Dataset final Ecuador + LATAM + EEUU
│       └── dataset_final.csv
│
├── scraping/                 # Pipeline de recolección de datos
│   ├── extracting.py                 # Scraper original EPN
│   ├── extraccion_datos.ipynb        # Notebook exploración scraping EPN
│   ├── config.py                     # URLs y metadatos Grupo 2 (13 universidades)
│   ├── scraper_base.py               # Clase base: fetch + BeautifulSoup + Claude API
│   └── pipeline.py                   # Entrada principal del pipeline
│
├── analysis/                 # Análisis NLP y similitud
│   ├── tfidf.py                      # Representación TF-IDF
│   ├── embeddings.py                 # BETO, Jina, E5
│   ├── similarity.py                 # Matriz de distancias coseno
│   └── dendrogram.py                 # Clustering jerárquico y visualización
│
├── notebooks/                # Exploración y análisis interactivo
│   └── exploracion.ipynb
│
├── logs/                     # Logs de ejecución del pipeline
├── requirements.txt
└── README.md
```

## Metodología de recolección (Ecuador)

Las carreras ecuatorianas se dividieron en 3 grupos según la complejidad de extracción:

| Grupo | Universidades                                                                   | Carreras | Método                                                |
| ----- | ------------------------------------------------------------------------------- | -------- | ----------------------------------------------------- |
| 1     | EPN, ESPOL, UPS, ESPOCH, UCE, UTM, UG, USFQ, UDLA, UTPL, ESPE, UCSG, PUCE, UTN  | 163      | Pipeline automático + recolección manual estructurada |
| 2     | UCUENCA, UCACUE, UDA, UEES, UIDE, ULEAM, UNACH, UNL, UPSE, UTA, UTC, UTEG, UTEQ | 104      | Pipeline automático (`scraping/pipeline.py`)          |
| 3     | 27 universidades pequeñas                                                       | 91       | Recolección manual estructurada                       |

### Campos recolectados por carrera

| Campo                | Descripción                    |
| -------------------- | ------------------------------ |
| `id`                 | Identificador único            |
| `pais`               | País de la universidad         |
| `universidad`        | Nombre completo                |
| `siglas`             | Siglas oficiales               |
| `nombre`             | Nombre de la carrera           |
| `epn_homologa`       | Carrera equivalente en la EPN  |
| `url`                | URL de la página oficial       |
| `metodo_recoleccion` | `html` (automático) o `manual` |
| `fecha_recoleccion`  | Fecha ISO de recolección       |
| `descripcion`        | Descripción general            |
| `perfil_ingreso`     | Perfil del aspirante           |
| `perfil_egreso`      | Competencias del graduado      |
| `perfil_profesional` | Campo laboral                  |

## Instalación

```bash
pip install -r requirements.txt
```

Además, necesitas una clave de API de Anthropic para el pipeline de extracción:

```bash
export ANTHROPIC_API_KEY="tu-clave-aqui"
```

## Uso del pipeline

```bash
# Procesar todas las universidades del Grupo 2
python scraping/pipeline.py --grupo 2

# Procesar solo algunas universidades
python scraping/pipeline.py --grupo 2 --siglas UCUENCA UDA

# Simular sin hacer requests (verificar configuración)
python scraping/pipeline.py --grupo 2 --dry-run

# Reanudar si se interrumpió (omite filas ya procesadas)
python scraping/pipeline.py --grupo 2
```

## Estado actual

- [x] Scraper EPN original
- [x] Dataset Ecuador Grupo 1 — 163 carreras
- [ ] Dataset Ecuador Grupo 2 — 104 carreras (pipeline listo, pendiente ejecución)
- [ ] Dataset Ecuador Grupo 3 — 91 carreras (llenado manual en progreso)
- [ ] Dataset LATAM + EEUU — 8 países OCDE (por definir)
- [ ] Análisis TF-IDF
- [ ] Embeddings BETO / Jina / E5
- [ ] Matriz de similitud
- [ ] Dendograma
