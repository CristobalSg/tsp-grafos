import math
from itertools import permutations
from math import asin, cos, radians, sin, sqrt
from typing import Callable, List, Tuple

try:
    from haversine import haversine as hv_distance, Unit  # type: ignore
    HAVERSINE_LIB_AVAILABLE = True
except ImportError:
    HAVERSINE_LIB_AVAILABLE = False


class Ciudad:
    """Entidad simple para representar una ciudad con nombre, región y coordenadas."""
    def __init__(self, nombre: str, region: str, lat: float, lon: float) -> None:
        self.nombre = nombre
        self.region = region
        self.lat = lat
        self.lon = lon


Ciudades: List[Ciudad] = [
    Ciudad("São Paulo", "Sudeste", -23.54750, -46.63611),
    Ciudad("Rio de Janeiro", "Sudeste", -22.90642, -43.18223),
    Ciudad("Belo Horizonte", "Sudeste", -19.92083, -43.93778),
    Ciudad("Curitiba", "Sur", -25.42778, -49.27306),
    Ciudad("Porto Alegre", "Sur", -30.03283, -51.23019),
    Ciudad("Salvador", "Nordeste", -12.97563, -38.49096),
    Ciudad("Recife", "Nordeste", -8.05389, -34.88111),
    Ciudad("Brasília", "Centro-Oeste", -15.77972, -47.92972),
]


def haversine_km(ciudad1: Ciudad, ciudad2: Ciudad) -> float:
    """
    Distancia entre dos ciudades usando la fórmula de Haversine.
    Adaptado de una implementación publicada por Clay en StackOverflow (CC BY-SA 4.0),
    ajustada para trabajar con la clase Ciudad y para entregar el resultado en kilómetros.
    """
    R = 6371.0  # radio de la Tierra en km
    dlat = radians(ciudad2.lat - ciudad1.lat)
    dlon = radians(ciudad2.lon - ciudad1.lon)
    lat1 = radians(ciudad1.lat)
    lat2 = radians(ciudad2.lat)
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c


def haversine_km_version_anterior(ciudad1: Ciudad, ciudad2: Ciudad) -> float:
    """Versión anterior basada en trigonometría esférica con radio 6371 km."""
    lat1, lon1, lat2, lon2 = map(
        math.radians, [ciudad1.lat, ciudad1.lon, ciudad2.lat, ciudad2.lon]
    )
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    radio_tierra_km = 6371.0
    return radio_tierra_km * c


def haversine_km_lib(ciudad1: Ciudad, ciudad2: Ciudad) -> float:
    """Usa la librería haversine para calcular la distancia en km."""
    if not HAVERSINE_LIB_AVAILABLE:
        raise ImportError(
            "La librería 'haversine' no está instalada; instala con `pip install haversine`."
        )
    return hv_distance((ciudad1.lat, ciudad1.lon), (ciudad2.lat, ciudad2.lon), unit=Unit.KILOMETERS)


def euclidiana_plana_km(ciudad1: Ciudad, ciudad2: Ciudad) -> float:
    """Aproximacion euclidiana usando grados a kilometros."""
    dlat = ciudad2.lat - ciudad1.lat
    dlon = ciudad2.lon - ciudad1.lon
    km_por_grado = 111.32
    ajuste_lon = math.cos(math.radians((ciudad1.lat + ciudad2.lat) / 2))
    return km_por_grado * math.sqrt(dlat**2 + (dlon * ajuste_lon) ** 2)


def matriz_distancias(
    ciudades: List[Ciudad], metodo: Callable[[Ciudad, Ciudad], float]
) -> List[List[float]]:
    """Crea matriz simetrica de distancias usando el metodo indicado."""
    n = len(ciudades)
    matriz = [[0.0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            distancia = metodo(ciudades[i], ciudades[j])
            matriz[i][j] = distancia
            matriz[j][i] = distancia
    return matriz


def imprimir_matriz(ciudades: List[Ciudad], matriz: List[List[float]]) -> None:
    encabezado = " " * 15 + "".join(f"{c.nombre:>15}" for c in ciudades)
    print(encabezado)
    for ciudad, fila in zip(ciudades, matriz):
        valores = "".join(f"{valor:15.2f}" for valor in fila)
        print(f"{ciudad.nombre:<15}{valores}")


def longitud_ruta(ruta: List[int], matriz: List[List[float]]) -> float:
    """Longitud total de una ruta cerrada (incluye retorno al origen)."""
    if len(ruta) < 2:
        return 0.0
    distancia = 0.0
    for i in range(len(ruta) - 1):
        distancia += matriz[ruta[i]][ruta[i + 1]]
    distancia += matriz[ruta[-1]][ruta[0]]  # regreso al inicio
    return distancia


def tsp_exhaustivo(
    matriz: List[List[float]],
    registrar: bool = False,
) -> Tuple[List[int], float, List[Tuple[List[int], float]]]:
    """
    Búsqueda exhaustiva (TSP) fijando la ciudad 0 como origen para reducir permutaciones.
    Si registrar=True, retorna tambien el historial de rutas evaluadas.
    """
    n = len(matriz)
    if n == 0:
        return [], 0.0, []
    mejor_ruta: List[int] = []
    mejor_dist = math.inf
    inicio = 0
    otros = list(range(1, n))
    historial: List[Tuple[List[int], float]] = []
    for perm in permutations(otros):
        ruta = [inicio, *perm]
        dist = longitud_ruta(ruta, matriz)
        if registrar:
            historial.append((ruta.copy(), dist))
        if dist < mejor_dist:
            mejor_dist = dist
            mejor_ruta = ruta
    return mejor_ruta, mejor_dist, historial


def vecino_mas_cercano(
    matriz: List[List[float]], inicio: int = 0, registrar: bool = False
) -> Tuple[List[int], float, List[Tuple[List[int], float]]]:
    """
    Heurística del vecino más cercano (Nearest Neighbor) partiendo de 'inicio'.
    Si registrar=True, retorna tambien el historial de rutas parciales evaluadas.
    """
    n = len(matriz)
    if n == 0:
        return [], 0.0, []
    historial: List[Tuple[List[int], float]] = []
    no_visitados = set(range(n))
    ruta = [inicio]
    no_visitados.remove(inicio)
    if registrar:
        historial.append((ruta.copy(), 0.0))
    actual = inicio
    while no_visitados:
        siguiente = min(no_visitados, key=lambda j: matriz[actual][j])
        ruta.append(siguiente)
        no_visitados.remove(siguiente)
        actual = siguiente
        if registrar:
            historial.append((ruta.copy(), longitud_ruta(ruta, matriz)))
    return ruta, longitud_ruta(ruta, matriz), historial
