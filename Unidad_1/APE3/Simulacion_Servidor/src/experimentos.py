"""Escenarios de la práctica e integración de teoría y simulación."""

import csv

from src.simulacion import simular_mm1
from src.teoria import metricas_teoricas

# Escenarios de la guía: mu es fijo y lam se acerca cada vez más a mu
ESCENARIOS = [
    {"escenario": 1, "lam": 2.0, "mu": 3.0, "condicion": "Sistema estable"},
    {"escenario": 2, "lam": 2.5, "mu": 3.0, "condicion": "Mayor utilizacion"},
    {"escenario": 3, "lam": 2.9, "mu": 3.0, "condicion": "Cerca de saturacion"},
]

# Duración de cada simulación (unidades de tiempo)
TIEMPO_SIM = 10000
# Semilla fija: cada ejecución da los mismos números (reproducibilidad)
SEMILLA = 42
# Columnas que se guardan en resultados/tabla.csv
COLUMNAS = [
    "escenario", "lam", "mu", "rho", "L", "Lq", "W", "Wq",
    "espera_promedio", "cola_promedio", "error_Wq_%", "error_Lq_%",
]

def escenarios_de_opcion(opcion, escenarios=ESCENARIOS):
    """Escenarios que corresponden a la opción del menú.

    1..n elige un solo escenario; n+1 elige todos.
    """
    if opcion == len(escenarios) + 1:
        return escenarios
    return [escenarios[opcion - 1]]

def error_porcentual(teorico, simulado):
    """Diferencia relativa entre el valor teórico y el simulado, en %."""
    return abs(teorico - simulado) / teorico * 100

def ejecutar_escenario(lam, mu):
    """Ejecuta un escenario: calcula la teoría, simula y compara ambos.

    Retorna un diccionario con las métricas teóricas, los resultados de la
    simulación (con los nombres que esperan las gráficas) y los errores %.
    """
    teoria = metricas_teoricas(lam,mu)
    sim = simular_mm1(lam,mu,TIEMPO_SIM,SEMILLA)
    return {
        "lam": lam,
        "mu": mu,
        # Desempaqueta rho, L, Lq, W y Wq en el mismo diccionario
        **teoria,
        # Se traducen los nombres de la simulación a los que usan las
        # gráficas y la tabla comparativa
        "espera_promedio": sim["Wq_simulado"],
        "cola_promedio": sim["cola_promedio_en_llegadas"],
        "clientes_atendidos": sim["clientes_atendidos"],
        "tiempos_espera": sim["tiempos_espera"],
        "muestras_cola": sim["muestras_cola"],
        "error_Wq_%": error_porcentual(teoria["Wq"], sim["Wq_simulado"]),
        "error_Lq_%": error_porcentual(teoria["Lq"], sim["cola_promedio_en_llegadas"]),
    }

def tabla_comparativa(resultados, ruta="resultados/tabla.csv"):
    """Guarda la tabla comparativa en CSV (la salida en consola está en src/consola.py)."""
    with open(ruta, "w", newline="") as archivo:
        # extrasaction="ignore" omite las listas largas (tiempos_espera,
        # muestras_cola) que no forman parte de la tabla
        escritor = csv.DictWriter(archivo, fieldnames=COLUMNAS, extrasaction="ignore")
        escritor.writeheader()
        escritor.writerows(resultados)
