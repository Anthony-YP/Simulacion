"""Análisis del período: teoría (Hull-Dobell) y medición empírica del ciclo."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from math import gcd

from .observacion import Observacion
from .parametros import ParametrosLCG


@dataclass(frozen=True)
class ResultadoHullDobell:
    """Evaluación del teorema de Hull-Dobell.

    Un LCG mixto tiene período completo (igual a m) si y solo si se cumplen:
      1. c y m son primos relativos: mcd(c, m) = 1.
      2. a - 1 es divisible por todos los factores primos de m.
      3. Si m es múltiplo de 4, a - 1 también es múltiplo de 4.
    """

    factores_primos_m: tuple[int, ...]
    mcd_c_m: int
    c_coprimo_con_m: bool
    a_menos_1_divisible_por_primos: bool
    a_menos_1_multiplo_de_4: bool

    @property
    def periodo_completo(self) -> bool:
        return self.c_coprimo_con_m and self.a_menos_1_divisible_por_primos and self.a_menos_1_multiplo_de_4


@dataclass(frozen=True)
class ResultadoCiclo:
    """Resultado de buscar el ciclo de una secuencia X(n+1) = f(X(n)).

    Como f actúa sobre un conjunto finito, tarde o temprano un valor se repite.
    X(0), ..., X(mu - 1) forman la "cola" previa al ciclo y, desde X(mu), los
    valores se repiten cada lambda pasos: X(n + lambda) = X(n) para n >= mu.

    Atributos:
        encontrado: True si se cerró el ciclo dentro de lo examinado.
        periodo: lambda, longitud del ciclo (None si no se encontró).
        inicio_ciclo: mu, posición del primer valor que pertenece al ciclo.
        pasos: valores examinados o evaluaciones de f realizadas.
    """

    encontrado: bool
    periodo: int | None
    inicio_ciclo: int | None
    pasos: int


class AnalizadorPeriodo:
    """Determina el período de un generador de forma teórica y empírica."""

    def verificar_hull_dobell(self, parametros: ParametrosLCG) -> ResultadoHullDobell:
        """Evalúa las tres condiciones del teorema con los parámetros dados."""
        a, c, m = parametros.a, parametros.c, parametros.m
        primos = self._factores_primos(m)
        mcd = gcd(c, m)
        return ResultadoHullDobell(
            factores_primos_m=primos,
            mcd_c_m=mcd,
            c_coprimo_con_m=mcd == 1,
            a_menos_1_divisible_por_primos=all((a - 1) % p == 0 for p in primos),
            # Si m no es múltiplo de 4, la condición 3 no aplica y se da por cumplida.
            a_menos_1_multiplo_de_4=m % 4 != 0 or (a - 1) % 4 == 0,
        )

    def buscar_repeticion(self, semilla: int, observaciones: Sequence[Observacion]) -> ResultadoCiclo:
        """Busca el primer valor repetido dentro de una muestra ya generada.

        Recorre X(0) = semilla, X(1), ..., X(N) guardando dónde apareció cada valor.
        Si X(j) ya había salido en la posición i, el ciclo empieza en i y mide
        j - i. Si no hay repeticiones, se concluye que mu + lambda > N.
        """
        primera_aparicion: dict[int, int] = {semilla: 0}
        for obs in observaciones:
            anterior = primera_aparicion.get(obs.x)
            if anterior is not None:
                return ResultadoCiclo(True, obs.n - anterior, anterior, obs.n)
            primera_aparicion[obs.x] = obs.n
        return ResultadoCiclo(False, None, None, len(observaciones))

    def medir_periodo(
        self,
        transicion: Callable[[int], int],
        semilla: int,
        limite_pasos: int | None = None,
    ) -> ResultadoCiclo:
        """Mide lambda y mu con el algoritmo de Brent usando memoria constante.

        Sirve para cualquier función de transición, tenga o no cola antes del
        ciclo. Si la búsqueda alcanza `limite_pasos` evaluaciones de f sin cerrar
        el ciclo, se detiene y devuelve un resultado no encontrado.
        """
        # Fase 1 - longitud del ciclo (lambda). La tortuga espera fija mientras la
        # liebre avanza; si la liebre da `potencia` pasos sin alcanzarla, la tortuga
        # salta a la posición de la liebre y la potencia se duplica. Cuando se
        # encuentran, los pasos dados desde el último salto son el período.
        potencia = periodo = 1
        tortuga = semilla
        liebre = transicion(semilla)
        pasos = 1
        while tortuga != liebre:
            if limite_pasos is not None and pasos >= limite_pasos:
                return ResultadoCiclo(False, None, None, pasos)
            if potencia == periodo:
                tortuga = liebre
                potencia *= 2
                periodo = 0
            liebre = transicion(liebre)
            periodo += 1
            pasos += 1

        # Fase 2 - inicio del ciclo (mu). Dos punteros separados `periodo` pasos
        # avanzan juntos desde la semilla; donde coinciden por primera vez está el
        # primer valor que pertenece al ciclo.
        tortuga = liebre = semilla
        for _ in range(periodo):
            liebre = transicion(liebre)
        inicio = 0
        while tortuga != liebre:
            tortuga = transicion(tortuga)
            liebre = transicion(liebre)
            inicio += 1
        return ResultadoCiclo(True, periodo, inicio, pasos + periodo + 2 * inicio)

    @staticmethod
    def _factores_primos(numero: int) -> tuple[int, ...]:
        """Factores primos distintos de `numero` por división de prueba."""
        factores = []
        divisor = 2
        while divisor * divisor <= numero:
            if numero % divisor == 0:
                factores.append(divisor)
                while numero % divisor == 0:
                    numero //= divisor
            divisor += 1 if divisor == 2 else 2  # tras el 2 solo se prueban impares
        if numero > 1:
            factores.append(numero)  # lo que queda es un primo mayor que la raíz
        return tuple(factores)
