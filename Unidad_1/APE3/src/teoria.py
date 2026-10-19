"""Métricas teóricas del modelo de colas M/M/1.

Implementa las fórmulas de estado estacionario de una cola con llegadas de
Poisson (tasa lam), tiempos de servicio exponenciales (tasa mu) y un único
servidor. Estos valores son la referencia contra la que se compara la
simulación.
"""


def es_estable(lam, mu):
    """Indica si el sistema alcanza un estado estacionario.

    La cola solo es estable cuando los clientes llegan más despacio de lo que
    el servidor puede atenderlos (lam < mu, es decir, rho < 1). Si no, la cola
    crece sin límite.
    """
    return lam < mu


def metricas_teoricas(lam, mu):
    """Calcula las métricas teóricas del modelo M/M/1.

    Parámetros:
        lam: tasa promedio de llegada de clientes.
        mu: tasa promedio de servicio del servidor.

    Retorna:
        Diccionario con rho, L, Lq, W y Wq.

    Lanza ValueError si el sistema no es estable, porque con lam >= mu las
    fórmulas dividen por cero o dan valores negativos.
    """
    if not es_estable(lam, mu):
        raise ValueError("El sistema no es estable")
    return {
        # Utilización: fracción del tiempo que el servidor está ocupado.
        "rho": lam / mu,
        # Clientes promedio en el sistema (en cola + siendo atendidos).
        "L": lam / (mu - lam),
        # Clientes promedio esperando en la cola.
        "Lq": lam**2 / (mu * (mu - lam)),
        # Tiempo promedio que un cliente pasa en el sistema (espera + servicio).
        "W": 1 / (mu - lam),
        # Tiempo promedio que un cliente espera en la cola antes de ser atendido.
        "Wq": lam / (mu * (mu - lam)),
    }
