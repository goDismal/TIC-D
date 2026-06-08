import pandas as pd
import requests
from bs4 import BeautifulSoup

url_base = "https://webhistorico.epn.edu.ec"
main = url_base + "/oferta-academica/grado/ingenieria-tecnologia/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

#Solicitud a la pagina objetivo
response_base = requests.get(url_base, headers=headers)

#Verificación de si la solicitud fue exitosa
if response_base.status_code == 200:
    print("Solicitud exitosa")
else:
    print(f"Error en la solicitud: {response_base.status_code}")

#Solicitud al contenido objetivo
response_main = requests.get(main, headers=headers)

# Verificación de si la solicitud fue exitosa
if response_main.status_code == 200:
    print("Solicitud exitosa")
else:
    print(f"Error en la solicitud: {response_main.status_code}")

#Obtencion del contenido del HTML de la pagina objetivo
soup_main = BeautifulSoup(response_main.content, 'html.parser')

#Listas para almacenar la información que vamos a extraer
lista_urls = []
lista_carreras = []
lista_perfiles = []

#Extracción de los urls de carreras
urls_carreras = soup_main.select('.loc.mntl-link-list li a')













# Extraer los enlaces de las carreras de grado
soup = BeautifulSoup(response_base.text, "html.parser")

carreras = []
for a in soup.select("a[href*='/carreras-de-grado/']"):
    name = a.text.strip()
    href = base_url + a['href']
    carreras.append((name, href))

datos = []
for name, url in carreras:
    r2 = requests.get(url)
    print("Procesando:", href)
    s2 = BeautifulSoup(r2.text, "html.parser")
    # Intentar encontrar "Perfil de egreso" o "Perfil profesional"
    headers = s2.find_all(['h2','h3','h4'])
    texto = ""
    for h in headers:
        if "Perfil" in h.text:
            # luego obtener los siguientes <p> hasta otro header
            for sib in h.find_next_siblings():
                if sib.name and sib.name.startswith('h'):
                    break
                if sib.name == 'p':
                    texto += sib.get_text(separator=' ', strip=True) + "\n"
    datos.append({"carrera": name, "perfil_egreso": texto})

df = pd.DataFrame(datos)
df.to_csv("perfiles_egreso.csv", index=False)
