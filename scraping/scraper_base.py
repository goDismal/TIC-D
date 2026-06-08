"""
scraper_base.py — Clase base para scraping de páginas de carrera universitaria.

Flujo por carrera:
  1. fetch_html()       → descarga el HTML con requests + timeout
  2. extract_text()     → limpia el HTML con BeautifulSoup (elimina nav, header, footer, scripts)
  3. extract_fields()   → llama a Claude API para extraer los 4 campos objetivo
  4. build_record()     → construye el dict listo para CSV

Si la página falla (timeout, 4xx, 5xx) se registra el error en el log y el
registro queda con los campos vacíos y status="ERROR".
"""

import time
import logging
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from datetime import date
from bs4 import BeautifulSoup
import anthropic

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Claude client (API key viene del entorno ANTHROPIC_API_KEY) ───────────────
client = anthropic.Anthropic()

# ── Prompt del sistema ────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Eres un extractor de información académica. Se te entregará el texto
extraído de la página web de una carrera universitaria ecuatoriana.

Tu tarea es identificar y extraer exactamente cuatro campos:

1. descripcion      — Descripción general de la carrera (2-4 oraciones).
2. perfil_ingreso   — Perfil o requisitos del aspirante al ingresar.
                      Si no está explícito en el texto, responde exactamente:
                      "No especificado en la web."
3. perfil_egreso    — Competencias, resultados de aprendizaje u objetivos del graduado.
4. perfil_profesional — Campo laboral, escenario profesional o empleabilidad.

Responde ÚNICAMENTE con un objeto JSON válido, sin texto adicional, sin backticks,
sin comentarios. Ejemplo de formato:
{
  "descripcion": "...",
  "perfil_ingreso": "...",
  "perfil_egreso": "...",
  "perfil_profesional": "..."
}
"""

# ── Constantes ────────────────────────────────────────────────────────────────
REQUEST_TIMEOUT   = 20          # segundos
MAX_TEXT_CHARS    = 8_000       # caracteres de texto a enviar a Claude
DELAY_BETWEEN_REQ = 2.0         # segundos entre requests (cortesía al servidor)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; TesisBot/1.0; "
        "+https://github.com/tu-usuario/tesis-homologas)"
    )
}

# ── Clase base ────────────────────────────────────────────────────────────────
class CarreraScraper:
    """
    Extrae los cuatro campos objetivo de una página de carrera universitaria.
    """

    def fetch_html(self, url: str) -> str | None:
        """Descarga el HTML de la URL. Retorna None si falla."""
        try:
            resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT, verify=False)
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding or "utf-8"
            return resp.text
        except requests.RequestException as e:
            log.warning(f"  ✗ fetch falló [{url}]: {e}")
            return None

    def extract_text(self, html: str) -> str:
        """
        Limpia el HTML con BeautifulSoup:
          - elimina nav, header, footer, script, style, aside, form
          - extrae el texto plano del <main> o <body>
          - trunca a MAX_TEXT_CHARS para no exceder el contexto de Claude
        """
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["nav", "header", "footer", "script",
                          "style", "aside", "form", "noscript"]):
            tag.decompose()

        # Preferir <main> si existe, si no tomar todo el body
        main = soup.find("main") or soup.find("body") or soup
        text = main.get_text(separator="\n", strip=True)

        # Colapsar líneas en blanco múltiples
        lines = [ln for ln in text.splitlines() if ln.strip()]
        clean = "\n".join(lines)
        return clean[:MAX_TEXT_CHARS]

    def extract_fields(
        self,
        text: str,
        universidad: str,
        carrera: str,
    ) -> dict:
        """
        Llama a Claude API con el texto de la página y retorna los 4 campos.
        Si falla el parseo del JSON devuelve campos vacíos con nota de error.
        """
        import json, re

        prompt = (
            f"Universidad: {universidad}\n"
            f"Carrera: {carrera}\n\n"
            f"Texto extraído de la página web:\n\n{text}"
        )

        try:
            msg = client.messages.create(
                model="claude-opus-4-5",          # modelo estable para producción
                max_tokens=1_024,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = msg.content[0].text.strip()

            # Limpiar posibles backticks que el modelo añada
            raw = re.sub(r"```(?:json)?", "", raw).strip()
            parsed = json.loads(raw)

            return {
                "descripcion":        parsed.get("descripcion", ""),
                "perfil_ingreso":     parsed.get("perfil_ingreso", ""),
                "perfil_egreso":      parsed.get("perfil_egreso", ""),
                "perfil_profesional": parsed.get("perfil_profesional", ""),
            }

        except (json.JSONDecodeError, IndexError, KeyError) as e:
            log.error(f"  ✗ Claude parse error: {e}")
            return {
                "descripcion":        "",
                "perfil_ingreso":     "",
                "perfil_egreso":      "",
                "perfil_profesional": f"ERROR_PARSE: {e}",
            }
        except Exception as e:
            log.error(f"  ✗ Claude API error: {e}")
            return {
                "descripcion":        "",
                "perfil_ingreso":     "",
                "perfil_egreso":      "",
                "perfil_profesional": f"ERROR_API: {e}",
            }

    def scrape_carrera(
        self,
        universidad: str,
        siglas: str,
        nombre: str,
        epn_homologa: str,
        url: str,
        metodo: str = "html",
    ) -> dict:
        """
        Pipeline completo para una carrera.
        Retorna un dict con todos los campos listos para el CSV.
        """
        log.info(f"  → {siglas} | {nombre}")

        base_record = {
            "universidad":        universidad,
            "siglas":             siglas,
            "nombre":             nombre,
            "epn_homologa":       epn_homologa,
            "url":                url,
            "metodo_recoleccion": metodo,
            "fecha_recoleccion":  date.today().isoformat(),
            "descripcion":        "",
            "perfil_ingreso":     "No especificado en la web.",
            "perfil_egreso":      "",
            "perfil_profesional": "",
            "status":             "OK",
        }

        if metodo != "html":
            base_record["status"] = "MANUAL"
            return base_record

        html = self.fetch_html(url)
        if html is None:
            base_record["status"] = "ERROR_FETCH"
            return base_record

        text = self.extract_text(html)
        if len(text) < 100:
            log.warning(f"  ⚠ Texto muy corto ({len(text)} chars) — posible JS rendering")
            base_record["status"] = "WARN_SHORT"

        fields = self.extract_fields(text, universidad, nombre)
        base_record.update(fields)

        time.sleep(DELAY_BETWEEN_REQ)
        return base_record
