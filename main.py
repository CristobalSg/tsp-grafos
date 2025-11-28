"""Ejecuta comparación TSP (exhaustivo vs vecino más cercano) y genera gráficas."""
from typing import Callable, List, Tuple
import csv
from pathlib import Path
from time import perf_counter

from distancias import (
    Ciudad,
    Ciudades,
    euclidiana_plana_km,
    haversine_km,
    haversine_km_lib,
    haversine_km_version_anterior,
    imprimir_matriz,
    longitud_ruta,
    matriz_distancias,
    tsp_exhaustivo,
    vecino_mas_cercano,
)
from graficos import (
    animar_historial,
    graficar_ciudades,
    graficar_grafo_distancias,
    graficar_ruta,
    heatmap_matriz,
)


def main() -> None:
    """Calcula distancias, ejecuta algoritmos TSP y exporta gráficos e historiales."""
    dir_animaciones = Path("animaciones")
    dir_imagenes = Path("imagenes")
    dir_historiales = Path("historiales")
    for carpeta in (dir_animaciones, dir_imagenes, dir_historiales):
        carpeta.mkdir(parents=True, exist_ok=True)

    calculos: List[Tuple[str, Callable[[Ciudad, Ciudad], float]]] = [
        ("Haversine (StackOverflow)", haversine_km),
        ("Haversine (version anterior)", haversine_km_version_anterior),
        ("Haversine (libreria haversine)", haversine_km_lib),
        ("Euclidiana plana", euclidiana_plana_km),
    ]

    # Calculamos y graficamos solo la primera matriz (Haversine principal)
    print("Matriz de distancias Haversine (StackOverflow) (km)")
    t_inicio = perf_counter()
    matriz_haversine = matriz_distancias(Ciudades, haversine_km)
    tiempo_matriz = perf_counter() - t_inicio
    imprimir_matriz(Ciudades, matriz_haversine)

    # Algoritmo exhaustivo y heurística NN sobre matriz Haversine principal
    t_inicio = perf_counter()
    ruta_optima, dist_optima, historial_exhaustivo = tsp_exhaustivo(
        matriz_haversine, registrar=True
    )
    tiempo_exhaustivo = perf_counter() - t_inicio

    t_inicio = perf_counter()
    ruta_nn, dist_nn, historial_nn = vecino_mas_cercano(
        matriz_haversine, inicio=0, registrar=True
    )
    tiempo_nn = perf_counter() - t_inicio

    try:
        graficar_ciudades(Ciudades, filename=str(dir_imagenes / "mapa_ciudades.png"))
        heatmap_matriz(
            Ciudades,
            matriz_haversine,
            titulo="Heatmap distancias Haversine (StackOverflow)",
            filename=str(dir_imagenes / "heatmap_haversine.png"),
        )
        graficar_grafo_distancias(
            Ciudades,
            matriz_haversine,
            filename=str(dir_imagenes / "grafo_distancias.png"),
            vecinos=3,
        )
        graficar_ruta(
            Ciudades,
            ruta_optima,
            filename=str(dir_imagenes / "ruta_optima.png"),
            titulo="Ruta optima (exhaustivo)",
        )
        graficar_ruta(
            Ciudades,
            ruta_nn,
            filename=str(dir_imagenes / "ruta_nn.png"),
            titulo="Ruta heuristica (Vecino Mas Cercano)",
        )
        animar_historial(
            Ciudades,
            historial_exhaustivo,
            filename=str(dir_animaciones / "anim_exhaustivo.gif"),
            titulo="Exhaustivo",
            paso=10,
        )
        animar_historial(
            Ciudades,
            historial_nn,
            filename=str(dir_animaciones / "anim_vecino_mas_cercano.gif"),
            titulo="Vecino Mas Cercano",
            paso=1,
        )
    except ImportError as exc:
        print(f"No se pudieron generar las graficas: {exc}")
    except Exception as exc:  # pragma: no cover - fallo general de graficos
        print(f"Error generando graficas: {exc}")
    print()

    def nombres_ruta(ruta_indices):
        return " -> ".join(Ciudades[i].nombre for i in ruta_indices) + f" -> {Ciudades[ruta_indices[0]].nombre}"

    print("Ruta optima (exhaustivo, fija origen en primera ciudad):")
    print(f"{nombres_ruta(ruta_optima)} | Distancia: {dist_optima:.2f} km | Tiempo: {tiempo_exhaustivo*1000:.2f} ms")
    print("Ruta heuristica (Vecino Mas Cercano):")
    print(f"{nombres_ruta(ruta_nn)} | Distancia: {dist_nn:.2f} km | Tiempo: {tiempo_nn*1000:.2f} ms")
    print(f"Tiempo de creacion de matriz: {tiempo_matriz*1000:.2f} ms")
    print()

    # Guardar historiales para animaciones
    def guardar_historial(nombre_archivo: Path, historial):
        """Exporta a CSV el historial de rutas evaluadas."""
        with open(nombre_archivo, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["paso", "ruta_indices", "ruta_nombres", "distancia_km"])
            for paso, (ruta, dist) in enumerate(historial, start=1):
                writer.writerow(
                    [
                        paso,
                        "-".join(map(str, ruta)),
                        " -> ".join(Ciudades[i].nombre for i in ruta),
                        f"{dist:.2f}",
                    ]
                )

    guardar_historial(dir_historiales / "historial_exhaustivo.csv", historial_exhaustivo)
    guardar_historial(dir_historiales / "historial_vecino_mas_cercano.csv", historial_nn)

    # Bloque comentado para evitar impresiones adicionales de matrices de distancia.
    # Si se requiere comparar otros metodos, descomentar y ejecutar.
    # for nombre, funcion in calculos[1:]:
    #     print(f"Matriz de distancias {nombre} (km)")
    #     try:
    #         matriz = matriz_distancias(Ciudades, funcion)
    #         imprimir_matriz(Ciudades, matriz)
    #     except ImportError as exc:
    #         print(f"No se pudo calcular: {exc}")
    #     print()


if __name__ == "__main__":
    main()
