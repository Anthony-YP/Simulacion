"""VISTA - Salida en consola y archivo CSV.

La vista solo recibe resultados ya calculados por el modelo y los presenta.
"""

import csv
from pathlib import Path

from model.clima import ResultadoHora

ENCABEZADOS = ["Hora", "Humedad", "Nubosidad", "Temp.", "H", "N", "Tf", "Índice", "Estado"]


def mostrar_tabla(titulo: str, resultados: list[ResultadoHora]) -> None:
    """Imprime la tabla de la guía con columnas alineadas."""
    print(f"\n=== {titulo} ===")
    print(f"{'Hora':<6} {'Hum%':>5} {'Nub%':>5} {'T°C':>4} "
          f"{'H':>5} {'N':>5} {'Tf':>5} {'Índice':>7}  Estado")
    print("-" * 66)
    for r in resultados:
        print(f"{r.hora:<6} {r.humedad:>5.0f} {r.nubosidad:>5.0f} {r.temperatura:>4.0f} "
              f"{r.h:>5.2f} {r.n:>5.2f} {r.tf:>5.2f} {r.indice:>7.4f}  {r.estado}")


def mostrar_horas_lluvia(titulo: str, resultados: list[ResultadoHora]) -> None:
    """Responde el objetivo del problema: en qué horas puede llover."""
    horas = [r.hora for r in resultados if r.estado in ("Lluvia probable", "Lluvia")]
    print(f"{titulo}: posibilidad de lluvia en {', '.join(horas) or 'ninguna hora'}")


def mostrar_tasas(info: list[tuple[float, float, float]]) -> None:
    """Imprime r, P(24) y el tiempo de duplicación / vida media."""
    print("\n=== Modelo exponencial P(t) = P0·e^(rt), P0 = 100 ===")
    print(f"{'r':>6} {'P(24)':>10} {'t dup / t½ (h)':>16}  Comportamiento")
    for r, p_final, t_mitad in info:
        tipo = "Crecimiento" if r > 0 else "Decrecimiento" if r < 0 else "Constante"
        t_txt = "—" if t_mitad == float("inf") else f"{t_mitad:.2f}"
        print(f"{r:>6.2f} {p_final:>10.2f} {t_txt:>16}  {tipo}")


def guardar_csv(resultados: list[ResultadoHora], ruta: Path) -> None:
    """Guarda la tabla completa en CSV para el informe."""
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(ENCABEZADOS)
        for r in resultados:
            escritor.writerow([r.hora, r.humedad, r.nubosidad, r.temperatura,
                               f"{r.h:.2f}", f"{r.n:.2f}", f"{r.tf:.2f}",
                               f"{r.indice:.4f}", r.estado])
