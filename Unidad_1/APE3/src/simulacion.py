"""Simulación de eventos discretos de una cola M/M/1 con SimPy.

El reloj de SimPy no avanza segundo a segundo: salta de un evento al
siguiente (una llegada, el inicio o el fin de una atención).
"""

import simpy
import numpy as np

from src.teoria import es_estable


def simular(lam, mu, tiempo_simulacion=1000, semilla=42):
    """
    Cola M/M/1 con un unico servidor

    Parametros:
        lam: tasa promedio de llegada de clientes.
        mu: tasa promedio de servicio.
        tiempo_simulacion: duracion de la simulacion.
        semilla: semilla para reproducir la simulacion.

    Retorna:
        Diccionario con los resultados de la simulacion.
    """

    # Validar parametros
    if lam <= 0 or mu <= 0:
        raise ValueError("Las tasas deben ser mayores que cero.")

    if tiempo_simulacion <= 0:
        raise ValueError("El tiempo de simulacion debe ser positivo.")

    if not es_estable(lam, mu):
        raise ValueError("El sistema no es estable.") 

    # Generador de numeros aleatorios (con la misma semilla se obtienen
    # exactamente los mismos resultados)
    rng = np.random.default_rng(semilla)

    # Crear entorno y servidor: el Resource con capacidad 1 es el unico
    # servidor; SimPy atiende sus solicitudes en orden de llegada (FIFO)
    env = simpy.Environment()
    servidor = simpy.Resource(env, capacity=1)

    # Variables de la simulacion
    tiempos_espera = []   # espera en cola de cada cliente (para Wq)
    tiempos_sistema = []  # espera + servicio de cada cliente (para W)
    tamanos_cola = []     # cola que observa cada cliente al llegar (para Lq)
    muestras_cola = []    # pares (tiempo, tamano de la cola) para graficar

    clientes_llegados = 0
    clientes_atendidos = 0

    def atender_cliente(numero):

        """Llegada, espera y atencion de un cliente."""
        nonlocal clientes_atendidos

        llegada = env.now

        # Registrar cuantos clientes esperan al llegar. Por la propiedad PASTA
        # (las llegadas de Poisson ven el promedio temporal), el promedio de
        # estos valores estima Lq
        tamanos_cola.append(len(servidor.queue))
        muestras_cola.append((env.now, len(servidor.queue)))
        

        # Solicitar el servidor. "yield solicitud" pausa al cliente hasta que
        # le toque su turno; al salir del bloque "with" el servidor se libera
        with servidor.request() as solicitud:
            yield solicitud

            # Registrar inicio del servicio y tiempo de espera
            inicio_servicio = env.now
            tiempos_espera.append(inicio_servicio - llegada)

            # Registrar la cola cuando el cliente sale de ella
            muestras_cola.append((env.now, len(servidor.queue)))

            # Generar duracion aleatoria del servicio (exponencial con
            # media 1/mu; NumPy recibe la media, no la tasa)
            tiempo_servicio = rng.exponential(1 / mu)

            # Atender al cliente
            yield env.timeout(tiempo_servicio)

            # Registrar finalizacion
            tiempos_sistema.append(env.now - llegada)
            clientes_atendidos += 1

    def generar_clientes():
        """Genera clientes segun el proceso de llegadas."""
        nonlocal clientes_llegados

        while True:
            # Tiempo entre llegadas con distribucion exponencial de media
            # 1/lam (equivale a llegadas de Poisson con tasa lam)
            intervalo = rng.exponential(1 / lam)

            # Esperar hasta la siguiente llegada
            yield env.timeout(intervalo)

            # No admitir clientes fuera del periodo de simulacion
            if env.now >= tiempo_simulacion:
                break

            clientes_llegados += 1
            env.process(atender_cliente(clientes_llegados))

    # Iniciar la generacion de clientes
    env.process(generar_clientes())

    # Ejecutar la simulacion
    env.run(until=tiempo_simulacion)

    # Devolver estadisticas simuladas
    return {
        "clientes_llegados": clientes_llegados,
        "clientes_atendidos": clientes_atendidos,
        "clientes_pendientes": clientes_llegados - clientes_atendidos,
        "Wq_simulado": (
            float(np.mean(tiempos_espera))
            if tiempos_espera else 0.0
        ),
        "W_simulado": (
            float(np.mean(tiempos_sistema))
            if tiempos_sistema else 0.0
        ),
        "cola_promedio_en_llegadas": (
            float(np.mean(tamanos_cola))
            if tamanos_cola else 0.0
        ),
        "tiempo_simulacion": tiempo_simulacion,
        "tiempos_espera": tiempos_espera,
        "muestras_cola": muestras_cola,
    }

# Alias con el nombre acordado en el contrato entre modulos del proyecto
simular_mm1 = simular