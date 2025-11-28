from typing import List

try:
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
try:
    from matplotlib import animation

    MATPLOTLIB_ANIMATION_AVAILABLE = True
except Exception:  # pragma: no cover - si matplotlib no esta
    MATPLOTLIB_ANIMATION_AVAILABLE = False

try:
    import seaborn as sns  # type: ignore

    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False

from distancias import Ciudad


def graficar_ciudades(ciudades: List[Ciudad], filename: str = "mapa_ciudades.png") -> None:
    """
    Grafica las ciudades sobre un mapa real usando Cartopy.
    Incluye contorno de países, gridlines y etiquetas de ciudades.
    """
    try:
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature
        import matplotlib.pyplot as plt  # aseguramos referencia local
    except ImportError:
        raise ImportError("Falta 'cartopy'. Instala con: pip install cartopy")

    lats = [c.lat for c in ciudades]
    lons = [c.lon for c in ciudades]

    fig = plt.figure(figsize=(10, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())

    ax.add_feature(cfeature.LAND, facecolor="#f0f0f0")
    ax.add_feature(cfeature.OCEAN, facecolor="#cce6ff")
    ax.add_feature(cfeature.BORDERS, linewidth=0.8, edgecolor="black")
    ax.add_feature(cfeature.COASTLINE, linewidth=0.6)
    ax.add_feature(cfeature.LAKES, facecolor="#b0d6ff", edgecolor="none")
    ax.add_feature(cfeature.RIVERS, edgecolor="#77aadd", linewidth=0.5)

    min_lat, max_lat = min(lats) - 5, max(lats) + 5
    min_lon, max_lon = min(lons) - 5, max(lons) + 5
    ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())

    ax.scatter(lons, lats, s=80, color="red", edgecolors="black", transform=ccrs.PlateCarree())

    for c in ciudades:
        ax.text(
            c.lon + 0.2,
            c.lat + 0.2,
            c.nombre,
            fontsize=9,
            transform=ccrs.PlateCarree(),
        )

    gl = ax.gridlines(draw_labels=True, alpha=0.4, linestyle="--")
    gl.top_labels = False
    gl.right_labels = False

    plt.title("Ubicación geográfica de las ciudades")
    plt.savefig(filename, dpi=200, bbox_inches="tight")
    print(f"Mapa guardado en {filename}")
    plt.close()


def heatmap_matriz(
    ciudades: List[Ciudad],
    matriz: List[List[float]],
    titulo: str,
    filename: str = "heatmap_distancias.png",
) -> None:
    """Genera un mapa de calor de la matriz de distancias."""
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError(
            "La librería 'matplotlib' no está instalada; instala con `pip install matplotlib`."
        )
    etiquetas = [c.nombre for c in ciudades]
    plt.figure(figsize=(10, 8))
    if SEABORN_AVAILABLE:
        sns.heatmap(
            matriz,
            xticklabels=etiquetas,
            yticklabels=etiquetas,
            cmap="YlOrRd",
            square=True,
            cbar_kws={"label": "Distancia (km)"},
            annot=False,
        )
    else:
        plt.imshow(matriz, cmap="YlOrRd")
        plt.colorbar(label="Distancia (km)")
        plt.xticks(range(len(etiquetas)), etiquetas, rotation=45, ha="right")
        plt.yticks(range(len(etiquetas)), etiquetas)
    plt.title(titulo)
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    print(f"Heatmap guardado en {filename}")
    plt.close()


def graficar_ruta(
    ciudades: List[Ciudad],
    ruta_indices: List[int],
    filename: str = "ruta.png",
    titulo: str = "Ruta",
) -> None:
    """
    Grafica una ruta cerrada sobre mapa con Cartopy.
    """
    try:
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature
        import matplotlib.pyplot as plt  # referencia local
    except ImportError:
        raise ImportError("Falta 'cartopy'. Instala con: pip install cartopy")

    if not ruta_indices:
        raise ValueError("La ruta está vacía, no se puede graficar.")

    coords = [(ciudades[i].lon, ciudades[i].lat) for i in ruta_indices]
    coords.append(coords[0])  # cerrar ciclo

    lons = [lon for lon, _ in coords]
    lats = [lat for _, lat in coords]

    fig = plt.figure(figsize=(10, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())

    ax.add_feature(cfeature.LAND, facecolor="#f0f0f0")
    ax.add_feature(cfeature.OCEAN, facecolor="#cce6ff")
    ax.add_feature(cfeature.BORDERS, linewidth=0.8, edgecolor="black")
    ax.add_feature(cfeature.COASTLINE, linewidth=0.6)
    ax.add_feature(cfeature.LAKES, facecolor="#b0d6ff", edgecolor="none")
    ax.add_feature(cfeature.RIVERS, edgecolor="#77aadd", linewidth=0.5)

    ax.plot(lons, lats, color="red", linewidth=2, marker="o", markersize=6, transform=ccrs.PlateCarree())

    for idx in ruta_indices:
        c = ciudades[idx]
        ax.text(c.lon + 0.2, c.lat + 0.2, c.nombre, fontsize=9, transform=ccrs.PlateCarree())

    min_lat, max_lat = min(lats) - 5, max(lats) + 5
    min_lon, max_lon = min(lons) - 5, max(lons) + 5
    ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())

    gl = ax.gridlines(draw_labels=True, alpha=0.4, linestyle="--")
    gl.top_labels = False
    gl.right_labels = False

    plt.title(titulo)
    plt.savefig(filename, dpi=200, bbox_inches="tight")
    print(f"Ruta guardada en {filename}")
    plt.close()


def animar_historial(
    ciudades: List[Ciudad],
    historial,
    filename: str,
    titulo: str,
    paso: int = 1,
) -> None:
    """
    Genera una animacion (GIF) paso a paso a partir de un historial de rutas.
    Usa coordenadas planas lat/lon para simplificar.
    """
    if not (MATPLOTLIB_AVAILABLE and MATPLOTLIB_ANIMATION_AVAILABLE):
        raise ImportError("Matplotlib (con animation) no esta disponible.")
    if not historial:
        raise ValueError("El historial está vacío; no se puede animar.")
    if paso < 1:
        paso = 1

    # Reducimos frames si se solicita un paso mayor
    historial_filtrado = historial[::paso]
    if historial_filtrado[-1] is not historial[-1]:
        historial_filtrado.append(historial[-1])

    fig, ax = plt.subplots(figsize=(8, 8))
    lats = [c.lat for c in ciudades]
    lons = [c.lon for c in ciudades]
    ax.scatter(lons, lats, c="tab:blue", s=80, edgecolors="black")
    for c in ciudades:
        ax.text(c.lon + 0.2, c.lat + 0.2, c.nombre, fontsize=9)
    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")
    ax.grid(True, linestyle="--", alpha=0.4)

    line, = ax.plot([], [], color="red", linewidth=2, marker="o", markersize=6)

    def init():
        line.set_data([], [])
        ax.set_title(titulo)
        return (line,)

    def update(frame):
        ruta, dist = frame
        coords = [(ciudades[i].lon, ciudades[i].lat) for i in ruta]
        if len(coords) > 1:
            coords.append(coords[0])
        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        line.set_data(xs, ys)
        ax.set_title(f"{titulo} | paso {historial_filtrado.index(frame)+1}/{len(historial_filtrado)} | dist {dist:.2f} km")
        return (line,)

    writer = animation.PillowWriter(fps=2)
    ani = animation.FuncAnimation(
        fig, update, frames=historial_filtrado, init_func=init, blit=True
    )
    ani.save(filename, writer=writer)
    print(f"Animacion guardada en {filename}")
    plt.close(fig)


def graficar_grafo_distancias(
    ciudades: List[Ciudad],
    matriz: List[List[float]],
    filename: str = "grafo_distancias.png",
    vecinos: int = 3,
) -> None:
    """
    Representa la matriz de distancias como un grafo con layout de fuerza.
    Solo conecta cada ciudad con sus k vecinos mas cercanos para evitar ruido visual.
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError(
            "La librería 'matplotlib' no está instalada; instala con `pip install matplotlib`."
        )
    try:
        import networkx as nx  # type: ignore
    except ImportError:
        raise ImportError("Falta 'networkx'. Instala con: pip install networkx")

    n = len(ciudades)
    G = nx.Graph()
    for idx, c in enumerate(ciudades):
        G.add_node(idx, label=c.nombre)

    edges = set()
    for i in range(n):
        distancias = [(j, matriz[i][j]) for j in range(n) if i != j]
        distancias.sort(key=lambda x: x[1])
        for j, distancia in distancias[:vecinos]:
            edge = tuple(sorted((i, j)))
            edges.add((edge[0], edge[1], distancia))

    for u, v, dist in edges:
        G.add_edge(u, v, weight=dist)

    pesos = [d["weight"] for _, _, d in G.edges(data=True)]
    max_peso = max(pesos) if pesos else 1.0
    widths = [1.0 + 4.0 * (1 - (p / max_peso)) for p in pesos]

    inverso = {(u, v): 1 / (d["weight"] + 1e-6) for u, v, d in G.edges(data=True)}
    pos = nx.spring_layout(G, weight=None, seed=42)
    nx.set_edge_attributes(G, inverso, "inv_weight")
    pos = nx.spring_layout(G, weight="inv_weight", seed=42)

    plt.figure(figsize=(10, 8))
    nx.draw_networkx_nodes(G, pos, node_size=600, node_color="#1f77b4", edgecolors="black")
    nx.draw_networkx_labels(G, pos, labels={i: c.nombre for i, c in enumerate(ciudades)}, font_size=9)
    nx.draw_networkx_edges(G, pos, width=widths, edge_color="#999999")

    etiquetas = {(u, v): f"{d['weight']:.0f} km" for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=etiquetas, font_size=8, label_pos=0.5)

    plt.title("Grafo de distancias (k vecinos mas cercanos)")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(filename, dpi=200)
    print(f"Grafo guardado en {filename}")
    plt.close()
