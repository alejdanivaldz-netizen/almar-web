# Herramientas

## make_map.py — mapa de Ñeembucú
Genera el SVG del mapa de la sección "Zonas" a partir de límites oficiales.

Datos (no incluidos en el repo, se descargan aparte):
- geoBoundaries gbOpen, CC BY 4.0: `PRY/ADM1`, `PRY/ADM2`, `ARG/ADM1` (versión `_simplified`)
  desde https://media.githubusercontent.com/media/wmgeolab/geoBoundaries/main/releaseData/gbOpen/...

Uso: `pip install shapely` y `python3 make_map.py` en la carpeta con los GeoJSON.
Produce `neembucu.svg` (se pega dentro de `<div class="mapsvg">` en `index.html`)
y `pins.json` (posiciones en % de los pines de Pilar, Humaitá y Paso de Patria).
