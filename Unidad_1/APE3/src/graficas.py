"""Gráficas de los resultados de la simulación M/M/1.

Todas las funciones guardan la imagen en disco y cierran la figura, para que
main.py se ejecute de principio a fin sin abrir ventanas.
"""

import matplotlib
# Backend sin interfaz gráfica: dibuja directo a archivo (no abre ventanas)
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def graficar_cola(muestras_cola, titulo, ruta, hasta=200):
    """Dibuja el número de clientes en cola a lo largo del tiempo.

    Parámetros:
        muestras_cola: lista de pares (tiempo, clientes en cola).
        titulo: título de la gráfica.
        ruta: archivo .png donde se guarda.
        hasta: último instante a mostrar; la simulación completa es muy larga
            y se vería como una mancha.
    """
    visibles = [(t, n) for t, n in muestras_cola if t <= hasta]
    tiempos = [t for t, _ in visibles]
    tamanos = [n for _, n in visibles]
    plt.figure(figsize=(10, 4))
    # Gráfica escalonada: la cola cambia de golpe (de 2 a 3 clientes), no de
    # forma continua; where="post" mantiene cada valor hasta el siguiente cambio
    plt.step(tiempos, tamanos, where="post")
    plt.title(titulo)
    plt.xlabel("Tiempo")
    plt.ylabel("Clientes en cola")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(ruta)
    # Cerrar la figura libera memoria y evita que se mezcle con la siguiente
    plt.close()


def graficar_esperas(tiempos_espera, titulo, ruta):
    """Dibuja el histograma de los tiempos de espera, con el promedio marcado."""
    plt.figure(figsize=(8, 4))
    plt.hist(tiempos_espera, bins=30, edgecolor="black")
    # Línea vertical en la espera promedio, para compararla a simple vista con Wq
    plt.axvline(np.mean(tiempos_espera), color="red", linestyle="--", label="Promedio")
    plt.title(titulo)
    plt.xlabel("Tiempo de espera")
    plt.ylabel("Cantidad de clientes")
    plt.legend()
    plt.tight_layout()
    plt.savefig(ruta)
    plt.close()


def graficar_comparacion(tabla, ruta):
    """Dibuja barras de teórico vs. simulado para Wq y Lq en cada escenario.

    Parámetros:
        tabla: lista de diccionarios con las claves escenario, Wq,
            espera_promedio, Lq y cola_promedio.
        ruta: archivo .png donde se guarda.
    """
    etiquetas = [f"Esc. {fila['escenario']}" for fila in tabla]
    x = np.arange(len(tabla))
    ancho = 0.35
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
    # Se desplaza cada barra medio ancho a la izquierda (teórico) o a la
    # derecha (simulado) para que queden lado a lado
    ax1.bar(x - ancho / 2, [f["Wq"] for f in tabla], ancho, label="Teórico")
    ax1.bar(x + ancho / 2, [f["espera_promedio"] for f in tabla], ancho, label="Simulado")
    ax1.set_title("Tiempo promedio en cola (Wq)")
    ax2.bar(x - ancho / 2, [f["Lq"] for f in tabla], ancho, label="Teórico")
    ax2.bar(x + ancho / 2, [f["cola_promedio"] for f in tabla], ancho, label="Simulado")
    ax2.set_title("Clientes promedio en cola (Lq)")
    for ax in (ax1, ax2):
        ax.set_xticks(x)
        ax.set_xticklabels(etiquetas)
        ax.legend()
        ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(ruta)
    plt.close(fig)
