# tsp-grafos

## Ejecución rápida
1. Crear el entorno virtual: `python -m venv .venv`
2. Activar el entorno:
   - Linux/macOS: `source .venv/bin/activate`
   - Windows (PowerShell): `.\.venv\Scripts\Activate.ps1`
3. Instalar dependencias: `pip install -r requirements.txt`
4. Ejecutar el programa: `python main.py`

## Código fuente documentado
- Las funciones de cálculo (`distancias.py`) y visualización (`graficos.py`) incluyen docstrings descriptivos.
- `main.py` documenta el flujo general: construcción de matriz Haversine, ejecución de TSP exhaustivo y heurístico, y exporte de resultados.

## Datos utilizados
- Conjunto de 8 ciudades de Brasil con nombre, región y coordenadas geográficas embebidas en `distancias.py`.
- Durante la ejecución se generan historiales CSV en `historiales/`: `historial_exhaustivo.csv` y `historial_vecino_mas_cercano.csv` con las rutas evaluadas y sus distancias.

## Visualizaciones generadas
- Mapas y gráficos estáticos se guardan en `imagenes/`: `mapa_ciudades.png`, `heatmap_haversine.png`, `grafo_distancias.png`, `ruta_optima.png`, `ruta_nn.png`.
- Animaciones GIF del proceso se guardan en `animaciones/`: `anim_exhaustivo.gif` y `anim_vecino_mas_cercano.gif`.
- Para generar las gráficas se requieren las dependencias de visualización (`matplotlib`, `seaborn`, `cartopy`, `networkx`) instaladas en el entorno.
