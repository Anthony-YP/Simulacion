"""Modelo SIR: datos y población (Parte 1) y simulación con SimPy (Parte 2)."""

import random
from dataclasses import dataclass
from enum import Enum

import simpy


# ---------------------------------------------------------------------------
# PARTE 1 – Datos y población
# ---------------------------------------------------------------------------

class State(Enum):
    """Estados posibles de un individuo del modelo SIR."""

    SUSCEPTIBLE = "S"
    INFECTED = "I"
    RECOVERED = "R"


@dataclass(frozen=True)
class SIRParameters:
    """Parámetros comunes del modelo, los mismos en Python, Java y NetLogo."""

    population: int = 100
    initial_infected: int = 5
    beta: float = 0.30
    gamma: float = 0.10
    max_time: int = 100
    seed: int = 42


@dataclass(frozen=True)
class StepResult:
    """Conteo de S, I y R registrado en un instante de tiempo."""

    time: int
    susceptible: int
    infected: int
    recovered: int


class Population:
    """Conjunto de individuos S, I o R."""

    def __init__(self, size: int, initial_infected: int, rng: random.Random) -> None:
        self.size = size
        self._rng = rng
        self._states = [State.SUSCEPTIBLE] * size
        for index in rng.sample(range(size), initial_infected):
            self._states[index] = State.INFECTED

    def count(self) -> tuple[int, int, int]:
        """Devuelve (S, I, R)."""
        return (
            self._states.count(State.SUSCEPTIBLE),
            self._states.count(State.INFECTED),
            self._states.count(State.RECOVERED),
        )

    def snapshot(self) -> list[State]:
        """Copia del estado actual, para calcular los cambios de un paso sobre ella."""
        return list(self._states)

    def random_contact(self, index: int) -> int:
        """Índice de un individuo al azar, distinto de `index`."""
        # Se elige entre size - 1 posiciones y se salta `index`: una sola llamada al rng.
        contact = self._rng.randrange(self.size - 1)
        return contact + 1 if contact >= index else contact

    def set_state(self, index: int, state: State) -> None:
        self._states[index] = state


# ---------------------------------------------------------------------------
# PARTE 2 – Simulación con SimPy
# ---------------------------------------------------------------------------

class SIRSimulation:
    """Simulación del modelo SIR sobre SimPy.

    Atributos:
        params: Parámetros del modelo (población, beta, gamma, etc.).
        rng: Generador aleatorio con semilla fija (reproducibilidad).
        population: Estado actual de la población.
        env: Entorno de simulación de SimPy.
        results: Lista de StepResult registrados en cada instante.
    """

    def __init__(self, params: SIRParameters) -> None:
        self.params = params
        self.rng = random.Random(params.seed)
        self.population = Population(
            size=params.population,
            initial_infected=params.initial_infected,
            rng=self.rng,
        )
        self.env = simpy.Environment()
        self.results: list[StepResult] = []

    # Registro y lógica de un paso

    def _record(self) -> None:
        """Guarda el conteo actual de S, I, R en el instante actual."""
        susceptible, infected, recovered = self.population.count()
        self.results.append(
            StepResult(
                time=int(self.env.now),
                susceptible=susceptible,
                infected=infected,
                recovered=recovered,
            )
        )

    def _step(self) -> None:
        """Aplica un paso de contagio y recuperación sobre el snapshot.

        Los cambios se calculan sobre una copia del estado para evitar
        que un individuo contagiado en este paso pueda contagiar a otro
        dentro del mismo paso.
        """
        snapshot = self.population.snapshot()
        self._spread_infections(snapshot)
        self._recover_infected(snapshot)

    def _spread_infections(self, snapshot: list[State]) -> None:
        """Cada infectado elige un contacto al azar y lo contagia con prob. beta."""
        for index, state in enumerate(snapshot):
            if state != State.INFECTED:
                continue
            contact = self.population.random_contact(index)
            if snapshot[contact] != State.SUSCEPTIBLE:
                continue
            if self.rng.random() < self.params.beta:
                self.population.set_state(contact, State.INFECTED)

    def _recover_infected(self, snapshot: list[State]) -> None:
        """Cada infectado al inicio del paso se recupera con prob. gamma."""
        for index, state in enumerate(snapshot):
            if state != State.INFECTED:
                continue
            if self.rng.random() < self.params.gamma:
                self.population.set_state(index, State.RECOVERED)

    # Bucle de simulación y ejecución

    def _process(self):
        """Generador de SimPy: registra y avanza el tiempo hasta max_time."""
        while self.env.now < self.params.max_time:
            self._record()
            self._step()
            yield self.env.timeout(1)
        # Registro final en t = max_time (última fila del CSV)
        self._record()

    def run(self) -> list[StepResult]:
        """Ejecuta la simulación y devuelve la lista de resultados."""
        self.env.process(self._process())
        self.env.run()
        return self.results
