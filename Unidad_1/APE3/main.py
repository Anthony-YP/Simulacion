"""Punto de entrada: menú para simular los escenarios de la práctica M/M/1.

Uso: python main.py
Muestra un menú para elegir un escenario o todos. Imprime los resultados en
la consola, guarda las gráficas (y, con todos, la tabla comparativa) en la
carpeta resultados/ y espera Enter antes de volver al menú.
"""

import os

from src.consola import (
    CONSOLA,
    esperar_enter,
    mostrar_archivos,
    mostrar_escenario,
    mostrar_inestable,
    mostrar_menu,
    mostrar_resumen_escenarios,
    mostrar_tabla,
    pedir_opcion,
)
from src.experimentos import (
    ESCENARIOS,
    SEMILLA,
    TIEMPO_SIM,
    ejecutar_escenario,
    escenarios_de_opcion,
    tabla_comparativa,
)
from src.graficas import graficar_cola, graficar_comparacion, graficar_esperas
from src.teoria import es_estable


def simular(escenarios):
    """Simula los escenarios elegidos, muestra los resultados y genera los archivos."""
    resultados = []  # un diccionario por escenario simulado
    archivos = []    # rutas generadas, para listarlas al final
    pares = []       # (escenario, resultado) para el resumen lado a lado

    for esc in escenarios:
        n = esc["escenario"]
        lam = esc["lam"]
        mu = esc["mu"]

        # Si lam >= mu la cola crece sin límite: el escenario no se simula
        if not es_estable(lam, mu):
            mostrar_inestable(n, lam, mu)
            continue

        # Muestra una animación de carga mientras corre la simulación
        with CONSOLA.status(f"Simulando escenario {n}..."):
            r = ejecutar_escenario(lam, mu)
        r["escenario"] = n
        resultados.append(r)
        pares.append((esc, r))
        # Con un solo escenario se muestra el panel grande en el momento
        if len(escenarios) == 1:
            mostrar_escenario(esc, r)

        # Gráficas propias de cada escenario
        titulo = f"Escenario {n} (lam={lam}, mu={mu})"
        ruta_cola = f"resultados/cola_esc{n}.png"
        ruta_esperas = f"resultados/esperas_esc{n}.png"
        graficar_cola(r["muestras_cola"], titulo, ruta_cola)
        graficar_esperas(r["tiempos_espera"], titulo, ruta_esperas)
        archivos += [ruta_cola, ruta_esperas]

    # Con varios escenarios se muestran paneles compactos lado a lado
    if len(escenarios) > 1 and pares:
        mostrar_resumen_escenarios(pares)

    # La comparación solo tiene sentido con más de un escenario
    if len(resultados) > 1:
        tabla_comparativa(resultados)
        graficar_comparacion(resultados, "resultados/comparacion.png")
        archivos += ["resultados/comparacion.png", "resultados/tabla.csv"]
        mostrar_tabla(resultados)

    if archivos:
        mostrar_archivos(archivos)


def main():
    """Muestra el menú y simula lo elegido hasta que el usuario sale."""
    os.makedirs("resultados", exist_ok=True)

    try:
        while True:
            # Se limpia la pantalla para que los resultados no se acumulen
            CONSOLA.clear()
            mostrar_menu(ESCENARIOS, TIEMPO_SIM, SEMILLA)
            opcion = pedir_opcion(ESCENARIOS)
            if opcion == 0:
                break
            simular(escenarios_de_opcion(opcion))
            esperar_enter()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C o fin de la entrada: se sale sin mostrar el error
        CONSOLA.print()
    CONSOLA.print("[bold]Hasta luego.[/bold]")


# Solo se ejecuta al correr "python main.py", no al importar este archivo
if __name__ == "__main__":
    main()
