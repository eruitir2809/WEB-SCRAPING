# WEB-SCRAPING

Proyecto de final de grado de DAM

## Descripción

Este proyecto consiste en la realización de un scraper web desarrollado en Python, como parte del proyecto final para la titulación de Desarrollo de Aplicaciones Multiplataforma (DAM). El objetivo principal es extraer información de sitios web de manera automatizada para su posterior análisis o utilización en otros sistemas.

## Características principales

- Extracción automática de datos de páginas web.
- Procesamiento y limpieza de la información obtenida.
- Estructuración de los datos en formatos útiles (CSV, JSON, etc.).
- Modularidad para adaptar el scraper a diferentes sitios web.
- Manejo de posibles bloqueos o restricciones de los sitios objetivo.
- Facilidad de configuración y personalización de los parámetros de scraping.

## Tecnologías utilizadas

- **Python** (100%)
- Librerías principales:
  - `requests`
  - `BeautifulSoup`
  - `pandas`
  - `lxml`
  - `json`
  - Otras dependencias según necesidades específicas del scraping

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/eruitir2809/WEB-SCRAPING.git
   ```
2. Accede al directorio del proyecto:
   ```bash
   cd WEB-SCRAPING
   ```
3. Instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

1. Configura los parámetros de scraping en el archivo de configuración o en el script principal.
2. Ejecuta el scraper:
   ```bash
   python main.py
   ```
3. Los datos extraídos estarán disponibles en la carpeta de salida especificada (por ejemplo, `output/`).

## Estructura del proyecto

```
WEB-SCRAPING/
│
├── main.py
├── requirements.txt
├── modules/
│   └── # Módulos auxiliares para scraping, limpieza, exportación, etc.
├── output/
│   └── # Archivos generados con los datos extraídos
└── README.md
```

## Licencia

Este proyecto se distribuye bajo la licencia MIT.

## Autor

- Enrique Ruiz Tirado
