"""
config.py — Configuración central del pipeline de recolección de datos.

Define las universidades objetivo, sus URLs de carrera y metadatos necesarios
para el scraping. Cada entrada sigue el esquema:
    {
        "siglas":       Siglas oficiales de la universidad
        "nombre":       Nombre completo
        "financiamiento": Pública / Particular cofinanciada / Particular autofinanciada
        "carreras": [
            {
                "nombre":   Nombre de la carrera en esa universidad
                "epn_homologa": Carrera equivalente en la EPN
                "url":      URL directa a la página de la carrera
                "metodo":   "html" | "pdf" | "manual"
                            html  → se hace fetch de la página y se extrae con BeautifulSoup + Claude API
                            pdf   → se descarga el PDF brochure y se extrae con pdfplumber
                            manual → datos recolectados manualmente (se documenta la fuente)
            }
        ]
    }
"""

GRUPO2 = [
    {
        "siglas": "UCUENCA",
        "nombre": "Universidad de Cuenca",
        "financiamiento": "Pública",
        "carreras": [
            {"nombre": "ADMINISTRACIÓN DE EMPRESAS",   "epn_homologa": "Administración de Empresas",          "url": "https://www.ucuenca.edu.ec/oferta-academica/carreras-presenciales/administracion-de-empresas",    "metodo": "html"},
            {"nombre": "COMPUTACIÓN",                  "epn_homologa": "Ciencias de la Computación",           "url": "https://www.ucuenca.edu.ec/oferta-academica/carreras-presenciales/computacion",                   "metodo": "html"},
            {"nombre": "ECONOMÍA",                     "epn_homologa": "Economía",                             "url": "https://www.ucuenca.edu.ec/oferta-academica/carreras-presenciales/economia",                      "metodo": "html"},
            {"nombre": "ELECTRICIDAD",                 "epn_homologa": "Ingeniería Eléctrica",                 "url": "https://www.ucuenca.edu.ec/oferta-academica/carreras-presenciales/ingenieria-electrica",          "metodo": "html"},
            {"nombre": "INGENIERÍA AMBIENTAL",         "epn_homologa": "Ingeniería Ambiental",                 "url": "https://www.ucuenca.edu.ec/oferta-academica/carreras-presenciales/ingenieria-ambiental",          "metodo": "html"},
            {"nombre": "INGENIERÍA CIVIL",             "epn_homologa": "Ingeniería Civil",                     "url": "https://www.ucuenca.edu.ec/oferta-academica/carreras-presenciales/ingenieria-civil",              "metodo": "html"},
            {"nombre": "INGENIERÍA INDUSTRIAL",        "epn_homologa": "Ingeniería de la Producción",          "url": "https://www.ucuenca.edu.ec/oferta-academica/carreras-presenciales/ingenieria-industrial",          "metodo": "html"},
            {"nombre": "INGENIERÍA QUÍMICA",           "epn_homologa": "Ingeniería Química",                   "url": "https://www.ucuenca.edu.ec/oferta-academica/carreras-presenciales/ingenieria-quimica",            "metodo": "html"},
            {"nombre": "TELECOMUNICACIONES",           "epn_homologa": "Telecomunicaciones",                   "url": "https://www.ucuenca.edu.ec/oferta-academica/carreras-presenciales/telecomunicaciones",            "metodo": "html"},
        ]
    },
    {
        "siglas": "UCACUE",
        "nombre": "Universidad Católica de Cuenca",
        "financiamiento": "Particular cofinanciada",
        "carreras": [
            {"nombre": "ADMINISTRACIÓN DE EMPRESAS",          "epn_homologa": "Administración de Empresas",   "url": "https://www.ucacue.edu.ec/carreras/administracion-de-empresas/",         "metodo": "html"},
            {"nombre": "ECONOMÍA",                            "epn_homologa": "Economía",                    "url": "https://www.ucacue.edu.ec/carreras/economia/",                            "metodo": "html"},
            {"nombre": "ELECTRICIDAD",                        "epn_homologa": "Ingeniería Eléctrica",        "url": "https://www.ucacue.edu.ec/carreras/electricidad/",                        "metodo": "html"},
            {"nombre": "INGENIERÍA AMBIENTAL",                "epn_homologa": "Ingeniería Ambiental",        "url": "https://www.ucacue.edu.ec/carreras/ingenieria-ambiental/",                "metodo": "html"},
            {"nombre": "INGENIERÍA CIVIL",                    "epn_homologa": "Ingeniería Civil",            "url": "https://www.ucacue.edu.ec/carreras/ingenieria-civil/",                    "metodo": "html"},
            {"nombre": "INGENIERÍA INDUSTRIAL",               "epn_homologa": "Ingeniería de la Producción", "url": "https://www.ucacue.edu.ec/carreras/ingenieria-industrial/",               "metodo": "html"},
            {"nombre": "ROBÓTICA E INTELIGENCIA ARTIFICIAL",  "epn_homologa": "Ciencias de Datos e IA",      "url": "https://www.ucacue.edu.ec/carreras/robotica-e-inteligencia-artificial/",  "metodo": "html"},
            {"nombre": "SISTEMAS DE INFORMACIÓN",             "epn_homologa": "Ingeniería en Sistemas de Información", "url": "https://www.ucacue.edu.ec/carreras/sistemas-de-informacion/",  "metodo": "html"},
            {"nombre": "SOFTWARE",                            "epn_homologa": "Ingeniería en Software",      "url": "https://www.ucacue.edu.ec/carreras/software/",                            "metodo": "html"},
        ]
    },
    {
        "siglas": "UDA",
        "nombre": "Universidad del Azuay",
        "financiamiento": "Particular cofinanciada",
        "carreras": [
            {"nombre": "ADMINISTRACIÓN DE EMPRESAS",    "epn_homologa": "Administración de Empresas",  "url": "https://www.uazuay.edu.ec/estudios/ingenieria-y-negocios/administracion-de-empresas",      "metodo": "html"},
            {"nombre": "COMPUTACIÓN",                   "epn_homologa": "Ciencias de la Computación",  "url": "https://www.uazuay.edu.ec/estudios/ingenieria-y-negocios/ingenieria-en-sistemas",           "metodo": "html"},
            {"nombre": "ECONOMÍA",                      "epn_homologa": "Economía",                    "url": "https://www.uazuay.edu.ec/estudios/ingenieria-y-negocios/economia",                         "metodo": "html"},
            {"nombre": "ELECTRÓNICA Y AUTOMATIZACIÓN",  "epn_homologa": "Electrónica y Automatización","url": "https://www.uazuay.edu.ec/estudios/ingenieria-y-negocios/electronica-y-automatizacion",    "metodo": "html"},
            {"nombre": "INGENIERÍA AMBIENTAL",          "epn_homologa": "Ingeniería Ambiental",        "url": "https://www.uazuay.edu.ec/estudios/ingenieria-y-negocios/ingenieria-ambiental",             "metodo": "html"},
            {"nombre": "INGENIERÍA CIVIL",              "epn_homologa": "Ingeniería Civil",            "url": "https://www.uazuay.edu.ec/estudios/ingenieria-y-negocios/ingenieria-civil",                 "metodo": "html"},
            {"nombre": "INGENIERÍA DE LA PRODUCCIÓN",   "epn_homologa": "Ingeniería de la Producción", "url": "https://www.uazuay.edu.ec/estudios/ingenieria-y-negocios/ingenieria-de-la-produccion",     "metodo": "html"},
        ]
    },
    {
        "siglas": "UEES",
        "nombre": "Universidad de Especialidades Espíritu Santo - UEES",
        "financiamiento": "Particular autofinanciada",
        "carreras": [
            {"nombre": "ADMINISTRACIÓN DE EMPRESAS",                    "epn_homologa": "Administración de Empresas",   "url": "https://www.uees.edu.ec/carreras/administracion-de-empresas/",                              "metodo": "html"},
            {"nombre": "CIENCIA DE DATOS",                              "epn_homologa": "Ciencias de Datos e IA",       "url": "https://www.uees.edu.ec/carreras/ciencia-de-datos/",                                        "metodo": "html"},
            {"nombre": "COMPUTACIÓN",                                   "epn_homologa": "Ciencias de la Computación",   "url": "https://www.uees.edu.ec/carreras/computacion/",                                             "metodo": "html"},
            {"nombre": "DESARROLLO, OPERACIÓN Y SEGURIDAD DE SOFTWARE", "epn_homologa": "Ingeniería en Software",       "url": "https://www.uees.edu.ec/carreras/desarrollo-operacion-y-seguridad-de-software/",           "metodo": "html"},
            {"nombre": "ECONOMÍA",                                      "epn_homologa": "Economía",                     "url": "https://www.uees.edu.ec/carreras/economia/",                                               "metodo": "html"},
            {"nombre": "INGENIERÍA AMBIENTAL",                          "epn_homologa": "Ingeniería Ambiental",         "url": "https://www.uees.edu.ec/carreras/ingenieria-ambiental/",                                    "metodo": "html"},
            {"nombre": "INGENIERÍA CIVIL",                              "epn_homologa": "Ingeniería Civil",             "url": "https://www.uees.edu.ec/carreras/ingenieria-civil/",                                        "metodo": "html"},
            {"nombre": "INGENIERÍA INDUSTRIAL",                         "epn_homologa": "Ingeniería de la Producción",  "url": "https://www.uees.edu.ec/carreras/ingenieria-industrial/",                                   "metodo": "html"},
            {"nombre": "TELECOMUNICACIONES",                            "epn_homologa": "Telecomunicaciones",           "url": "https://www.uees.edu.ec/carreras/telecomunicaciones/",                                      "metodo": "html"},
        ]
    },
    {
        "siglas": "UIDE",
        "nombre": "Universidad Internacional del Ecuador (UIDE)",
        "financiamiento": "Particular autofinanciada",
        "carreras": [
            {"nombre": "ADMINISTRACIÓN DE EMPRESAS", "epn_homologa": "Administración de Empresas",         "url": "https://www.uide.edu.ec/carreras/administracion-de-empresas/",       "metodo": "html"},
            {"nombre": "AGROINDUSTRIA",               "epn_homologa": "Agroindustria",                     "url": "https://www.uide.edu.ec/carreras/agroindustria/",                     "metodo": "html"},
            {"nombre": "ECONOMÍA",                   "epn_homologa": "Economía",                          "url": "https://www.uide.edu.ec/carreras/economia/",                          "metodo": "html"},
            {"nombre": "INGENIERÍA CIVIL",           "epn_homologa": "Ingeniería Civil",                  "url": "https://www.uide.edu.ec/carreras/ingenieria-civil/",                  "metodo": "html"},
            {"nombre": "INGENIERÍA INDUSTRIAL",      "epn_homologa": "Ingeniería de la Producción",       "url": "https://www.uide.edu.ec/carreras/ingenieria-industrial/",             "metodo": "html"},
            {"nombre": "MECATRÓNICA",                "epn_homologa": "Mecatrónica",                       "url": "https://www.uide.edu.ec/carreras/mecatronica/",                       "metodo": "html"},
            {"nombre": "SISTEMAS DE INFORMACIÓN",    "epn_homologa": "Ingeniería en Sistemas de Información", "url": "https://www.uide.edu.ec/carreras/sistemas-de-informacion/",    "metodo": "html"},
        ]
    },
    {
        "siglas": "ULEAM",
        "nombre": "Universidad Laica \"Eloy Alfaro\" de Manabí",
        "financiamiento": "Pública",
        "carreras": [
            {"nombre": "ADMINISTRACIÓN DE EMPRESAS", "epn_homologa": "Administración de Empresas",  "url": "https://www.uleam.edu.ec/carreras/administracion-de-empresas/",  "metodo": "html"},
            {"nombre": "AGROINDUSTRIA",               "epn_homologa": "Agroindustria",               "url": "https://www.uleam.edu.ec/carreras/agroindustria/",               "metodo": "html"},
            {"nombre": "ECONOMÍA",                   "epn_homologa": "Economía",                    "url": "https://www.uleam.edu.ec/carreras/economia/",                    "metodo": "html"},
            {"nombre": "ELECTRICIDAD",               "epn_homologa": "Ingeniería Eléctrica",        "url": "https://www.uleam.edu.ec/carreras/electricidad/",                "metodo": "html"},
            {"nombre": "INGENIERÍA AMBIENTAL",       "epn_homologa": "Ingeniería Ambiental",        "url": "https://www.uleam.edu.ec/carreras/ingenieria-ambiental/",        "metodo": "html"},
            {"nombre": "INGENIERÍA CIVIL",           "epn_homologa": "Ingeniería Civil",            "url": "https://www.uleam.edu.ec/carreras/ingenieria-civil/",            "metodo": "html"},
            {"nombre": "INGENIERÍA INDUSTRIAL",      "epn_homologa": "Ingeniería de la Producción", "url": "https://www.uleam.edu.ec/carreras/ingenieria-industrial/",       "metodo": "html"},
            {"nombre": "SOFTWARE",                   "epn_homologa": "Ingeniería en Software",      "url": "https://www.uleam.edu.ec/carreras/software/",                    "metodo": "html"},
        ]
    },
    {
        "siglas": "UNACH",
        "nombre": "Universidad Nacional de Chimborazo",
        "financiamiento": "Pública",
        "carreras": [
            {"nombre": "ADMINISTRACIÓN DE EMPRESAS",            "epn_homologa": "Administración de Empresas",  "url": "https://www.unach.edu.ec/oferta-academica/administracion-de-empresas/",             "metodo": "html"},
            {"nombre": "AGROINDUSTRIA",                         "epn_homologa": "Agroindustria",               "url": "https://www.unach.edu.ec/oferta-academica/agroindustria/",                         "metodo": "html"},
            {"nombre": "CIENCIA DE DATOS E INTELIGENCIA ARTIFICIAL", "epn_homologa": "Ciencias de Datos e IA", "url": "https://www.unach.edu.ec/oferta-academica/ciencia-de-datos/",                     "metodo": "html"},
            {"nombre": "ECONOMÍA",                              "epn_homologa": "Economía",                    "url": "https://www.unach.edu.ec/oferta-academica/economia/",                              "metodo": "html"},
            {"nombre": "INGENIERÍA AMBIENTAL",                  "epn_homologa": "Ingeniería Ambiental",        "url": "https://www.unach.edu.ec/oferta-academica/ingenieria-ambiental/",                  "metodo": "html"},
            {"nombre": "INGENIERÍA CIVIL",                      "epn_homologa": "Ingeniería Civil",            "url": "https://www.unach.edu.ec/oferta-academica/ingenieria-civil/",                      "metodo": "html"},
            {"nombre": "INGENIERÍA INDUSTRIAL",                 "epn_homologa": "Ingeniería de la Producción", "url": "https://www.unach.edu.ec/oferta-academica/ingenieria-industrial/",                 "metodo": "html"},
            {"nombre": "TELECOMUNICACIONES",                    "epn_homologa": "Telecomunicaciones",          "url": "https://www.unach.edu.ec/oferta-academica/telecomunicaciones/",                    "metodo": "html"},
        ]
    },
    {
        "siglas": "UNL",
        "nombre": "Universidad Nacional de Loja",
        "financiamiento": "Pública",
        "carreras": [
            {"nombre": "ADMINISTRACIÓN DE EMPRESAS",                                    "epn_homologa": "Administración de Empresas",  "url": "https://unl.edu.ec/administracion-de-empresas",          "metodo": "html"},
            {"nombre": "COMPUTACIÓN",                                                   "epn_homologa": "Ciencias de la Computación",  "url": "https://unl.edu.ec/computacion",                          "metodo": "html"},
            {"nombre": "ECONOMÍA",                                                      "epn_homologa": "Economía",                    "url": "https://unl.edu.ec/economia",                             "metodo": "html"},
            {"nombre": "ELECTRICIDAD",                                                  "epn_homologa": "Ingeniería Eléctrica",        "url": "https://unl.edu.ec/electricidad",                         "metodo": "html"},
            {"nombre": "INGENIERÍA AMBIENTAL",                                          "epn_homologa": "Ingeniería Ambiental",        "url": "https://unl.edu.ec/ingenieria-ambiental",                 "metodo": "html"},
            {"nombre": "INGENIERÍA EN GEOLOGÍA AMBIENTAL Y ORDENAMIENTO TERRITORIAL",   "epn_homologa": "Ingeniería en Geología",      "url": "https://unl.edu.ec/geologia-ambiental",                  "metodo": "html"},
            {"nombre": "TELECOMUNICACIONES",                                            "epn_homologa": "Telecomunicaciones",          "url": "https://unl.edu.ec/telecomunicaciones",                   "metodo": "html"},
        ]
    },
    {
        "siglas": "UPSE",
        "nombre": "Universidad Estatal Península de Santa Elena - UPSE",
        "financiamiento": "Pública",
        "carreras": [
            {"nombre": "ADMINISTRACIÓN DE EMPRESAS",        "epn_homologa": "Administración de Empresas",              "url": "https://www.upse.edu.ec/index.php/oferta-academica/administracion-de-empresas",          "metodo": "html"},
            {"nombre": "ECONOMÍA",                          "epn_homologa": "Economía",                                "url": "https://www.upse.edu.ec/index.php/oferta-academica/economia",                            "metodo": "html"},
            {"nombre": "ELECTRÓNICA Y AUTOMATIZACIÓN",      "epn_homologa": "Electrónica y Automatización",            "url": "https://www.upse.edu.ec/index.php/oferta-academica/electronica-y-automatizacion",         "metodo": "html"},
            {"nombre": "ELECTRÓNICA Y TELECOMUNICACIONES",  "epn_homologa": "Telecomunicaciones",                     "url": "https://www.upse.edu.ec/index.php/oferta-academica/electronica-y-telecomunicaciones",     "metodo": "html"},
            {"nombre": "INGENIERÍA CIVIL",                  "epn_homologa": "Ingeniería Civil",                        "url": "https://www.upse.edu.ec/index.php/oferta-academica/ingenieria-civil",                     "metodo": "html"},
            {"nombre": "INGENIERÍA INDUSTRIAL",             "epn_homologa": "Ingeniería de la Producción",             "url": "https://www.upse.edu.ec/index.php/oferta-academica/ingenieria-industrial",                "metodo": "html"},
            {"nombre": "PETRÓLEOS",                         "epn_homologa": "Ingeniería en Petróleos",                 "url": "https://www.upse.edu.ec/index.php/oferta-academica/petroleos",                           "metodo": "html"},
            {"nombre": "SOFTWARE",                          "epn_homologa": "Ingeniería en Software",                  "url": "https://www.upse.edu.ec/index.php/oferta-academica/software",                            "metodo": "html"},
            {"nombre": "TELECOMUNICACIONES",                "epn_homologa": "Telecomunicaciones",                      "url": "https://www.upse.edu.ec/index.php/oferta-academica/telecomunicaciones",                  "metodo": "html"},
        ]
    },
    {
        "siglas": "UTA",
        "nombre": "Universidad Técnica de Ambato",
        "financiamiento": "Pública",
        "carreras": [
            {"nombre": "ADMINISTRACIÓN DE EMPRESAS", "epn_homologa": "Administración de Empresas",  "url": "https://uta.edu.ec/v4.0/index.php/oferta-academica/administracion-empresas",   "metodo": "html"},
            {"nombre": "ECONOMÍA",                   "epn_homologa": "Economía",                    "url": "https://uta.edu.ec/v4.0/index.php/oferta-academica/economia",                   "metodo": "html"},
            {"nombre": "INGENIERÍA CIVIL",           "epn_homologa": "Ingeniería Civil",            "url": "https://uta.edu.ec/v4.0/index.php/oferta-academica/civil",                      "metodo": "html"},
            {"nombre": "INGENIERÍA INDUSTRIAL",      "epn_homologa": "Ingeniería de la Producción", "url": "https://uta.edu.ec/v4.0/index.php/oferta-academica/industrial",                  "metodo": "html"},
            {"nombre": "MECÁNICA",                   "epn_homologa": "Ingeniería en Mecánica",      "url": "https://uta.edu.ec/v4.0/index.php/oferta-academica/mecanica",                    "metodo": "html"},
            {"nombre": "SOFTWARE",                   "epn_homologa": "Ingeniería en Software",      "url": "https://uta.edu.ec/v4.0/index.php/oferta-academica/software",                    "metodo": "html"},
            {"nombre": "TELECOMUNICACIONES",         "epn_homologa": "Telecomunicaciones",          "url": "https://uta.edu.ec/v4.0/index.php/oferta-academica/telecomunicaciones",          "metodo": "html"},
        ]
    },
    {
        "siglas": "UTC",
        "nombre": "Universidad Técnica de Cotopaxi",
        "financiamiento": "Pública",
        "carreras": [
            {"nombre": "ADMINISTRACIÓN DE EMPRESAS", "epn_homologa": "Administración de Empresas",  "url": "https://www.utc.edu.ec/oferta-academica/administracion-de-empresas/",  "metodo": "html"},
            {"nombre": "AGROINDUSTRIA",               "epn_homologa": "Agroindustria",               "url": "https://www.utc.edu.ec/oferta-academica/agroindustria/",               "metodo": "html"},
            {"nombre": "ECONOMÍA",                   "epn_homologa": "Economía",                    "url": "https://www.utc.edu.ec/oferta-academica/economia/",                    "metodo": "html"},
            {"nombre": "ELECTRICIDAD",               "epn_homologa": "Ingeniería Eléctrica",        "url": "https://www.utc.edu.ec/oferta-academica/electricidad/",                "metodo": "html"},
            {"nombre": "INGENIERÍA AMBIENTAL",       "epn_homologa": "Ingeniería Ambiental",        "url": "https://www.utc.edu.ec/oferta-academica/ingenieria-ambiental/",        "metodo": "html"},
            {"nombre": "INGENIERÍA INDUSTRIAL",      "epn_homologa": "Ingeniería de la Producción", "url": "https://www.utc.edu.ec/oferta-academica/ingenieria-industrial/",       "metodo": "html"},
            {"nombre": "SOFTWARE",                   "epn_homologa": "Ingeniería en Software",      "url": "https://www.utc.edu.ec/oferta-academica/software/",                    "metodo": "html"},
        ]
    },
    {
        "siglas": "UTEG",
        "nombre": "Universidad Tecnológica Empresarial de Guayaquil",
        "financiamiento": "Particular autofinanciada",
        "carreras": [
            {"nombre": "ADMINISTRACIÓN DE EMPRESAS",    "epn_homologa": "Administración de Empresas",          "url": "https://www.uteg.edu.ec/carreras/administracion-de-empresas/",    "metodo": "html"},
            {"nombre": "ECONOMÍA",                      "epn_homologa": "Economía",                            "url": "https://www.uteg.edu.ec/carreras/economia/",                      "metodo": "html"},
            {"nombre": "GESTIÓN DE TELECOMUNICACIONES", "epn_homologa": "Telecomunicaciones",                  "url": "https://www.uteg.edu.ec/carreras/gestion-de-telecomunicaciones/", "metodo": "html"},
            {"nombre": "INGENIERÍA AMBIENTAL",          "epn_homologa": "Ingeniería Ambiental",                "url": "https://www.uteg.edu.ec/carreras/ingenieria-ambiental/",          "metodo": "html"},
            {"nombre": "INGENIERÍA INDUSTRIAL",         "epn_homologa": "Ingeniería de la Producción",         "url": "https://www.uteg.edu.ec/carreras/ingenieria-industrial/",         "metodo": "html"},
            {"nombre": "SISTEMAS DE INFORMACIÓN",       "epn_homologa": "Ingeniería en Sistemas de Información","url": "https://www.uteg.edu.ec/carreras/sistemas-de-informacion/",       "metodo": "html"},
            {"nombre": "SOFTWARE",                      "epn_homologa": "Ingeniería en Software",              "url": "https://www.uteg.edu.ec/carreras/software/",                      "metodo": "html"},
            {"nombre": "TELECOMUNICACIONES",            "epn_homologa": "Telecomunicaciones",                  "url": "https://www.uteg.edu.ec/carreras/telecomunicaciones/",            "metodo": "html"},
        ]
    },
    {
        "siglas": "UTEQ",
        "nombre": "Universidad Técnica Estatal de Quevedo",
        "financiamiento": "Pública",
        "carreras": [
            {"nombre": "ADMINISTRACIÓN DE EMPRESAS", "epn_homologa": "Administración de Empresas",  "url": "https://www.uteq.edu.ec/oferta-academica/administracion-de-empresas/",  "metodo": "html"},
            {"nombre": "AGROINDUSTRIA",               "epn_homologa": "Agroindustria",               "url": "https://www.uteq.edu.ec/oferta-academica/agroindustria/",               "metodo": "html"},
            {"nombre": "ECONOMÍA",                   "epn_homologa": "Economía",                    "url": "https://www.uteq.edu.ec/oferta-academica/economia/",                    "metodo": "html"},
            {"nombre": "ELECTRICIDAD",               "epn_homologa": "Ingeniería Eléctrica",        "url": "https://www.uteq.edu.ec/oferta-academica/electricidad/",                "metodo": "html"},
            {"nombre": "INGENIERÍA AMBIENTAL",       "epn_homologa": "Ingeniería Ambiental",        "url": "https://www.uteq.edu.ec/oferta-academica/ingenieria-ambiental/",        "metodo": "html"},
            {"nombre": "INGENIERÍA INDUSTRIAL",      "epn_homologa": "Ingeniería de la Producción", "url": "https://www.uteq.edu.ec/oferta-academica/ingenieria-industrial/",       "metodo": "html"},
            {"nombre": "MECÁNICA",                   "epn_homologa": "Ingeniería en Mecánica",      "url": "https://www.uteq.edu.ec/oferta-academica/mecanica/",                    "metodo": "html"},
            {"nombre": "SISTEMAS DE INFORMACIÓN",    "epn_homologa": "Ingeniería en Sistemas de Información", "url": "https://www.uteq.edu.ec/oferta-academica/sistemas-de-informacion/", "metodo": "html"},
            {"nombre": "SOFTWARE",                   "epn_homologa": "Ingeniería en Software",      "url": "https://www.uteq.edu.ec/oferta-academica/software/",                    "metodo": "html"},
        ]
    },
]

# Campos que se extraen de cada carrera
CAMPOS_OBJETIVO = [
    "descripcion",
    "perfil_ingreso",
    "perfil_egreso",
    "perfil_profesional",
]

# Campos del CSV final
CSV_COLUMNAS = [
    "universidad",
    "siglas",
    "nombre",
    "epn_homologa",
    "url",
    "metodo_recoleccion",
    "fecha_recoleccion",
    "descripcion",
    "perfil_ingreso",
    "perfil_egreso",
    "perfil_profesional",
]
