"""Verificación del modelo: python3 -m unittest discover -s tests -v"""
import math
import unittest

from montecarlo.modelo.estimador_pi import EstimadorPiMonteCarlo
from montecarlo.modelo.experimento import ExperimentoMonteCarlo
from montecarlo.modelo.generador_lcg import (
    PARAMETROS_NUMERICAL_RECIPES,
    GeneradorCongruencialLineal,
    ParametrosLCG,
)


class _GeneradorFijo:
    """Devuelve una lista conocida de números para comprobar el conteo a mano."""

    def __init__(self, numeros):
        self._numeros = iter(numeros)

    def siguiente(self):
        return next(self._numeros)


class PruebasGeneradorLCG(unittest.TestCase):
    def test_secuencia_calculada_a_mano(self):
        # a=5, c=3, m=16, X0=7: X1=(35+3)%16=6, X2=(30+3)%16=1, X3=(5+3)%16=8
        generador = GeneradorCongruencialLineal(ParametrosLCG(a=5, c=3, m=16, semilla=7))
        self.assertEqual([generador.siguiente_entero() for _ in range(3)], [6, 1, 8])

    def test_primer_valor_numerical_recipes(self):
        generador = GeneradorCongruencialLineal(PARAMETROS_NUMERICAL_RECIPES)
        esperado = (1_664_525 * 12_345 + 1_013_904_223) % 2**32
        self.assertEqual(generador.siguiente_entero(), esperado)

    def test_valores_en_intervalo_unitario(self):
        numeros = GeneradorCongruencialLineal(PARAMETROS_NUMERICAL_RECIPES).generar(10_000)
        self.assertTrue(all(0.0 <= u < 1.0 for u in numeros))

    def test_reiniciar_reproduce_la_secuencia(self):
        generador = GeneradorCongruencialLineal(PARAMETROS_NUMERICAL_RECIPES)
        primera = generador.generar(100)
        generador.reiniciar()
        self.assertEqual(primera, generador.generar(100))

    def test_parametros_invalidos(self):
        with self.assertRaises(ValueError):
            ParametrosLCG(a=0, c=1, m=16, semilla=1)
        with self.assertRaises(ValueError):
            ParametrosLCG(a=5, c=0, m=16, semilla=0)


class PruebasEstimador(unittest.TestCase):
    def test_conteo_de_puntos_conocidos(self):
        # U=0.5 -> coordenada 0 (centro, dentro); U=0.99 -> 0.98, el punto (0.98, 0.98) queda fuera.
        generador = _GeneradorFijo([0.5, 0.5, 0.99, 0.99, 0.5, 0.0])
        self.assertEqual(EstimadorPiMonteCarlo.contar_dentro(generador, 3), 2)  # (0,0) y (0,-1) dentro

    def test_formula_pi(self):
        self.assertAlmostEqual(EstimadorPiMonteCarlo.calcular_pi(785, 1000), 3.14)

    def test_muestreo_coincide_con_conteo(self):
        n = 5_000
        dentro = EstimadorPiMonteCarlo.contar_dentro(GeneradorCongruencialLineal(PARAMETROS_NUMERICAL_RECIPES), n)
        muestra = EstimadorPiMonteCarlo.muestrear_puntos(GeneradorCongruencialLineal(PARAMETROS_NUMERICAL_RECIPES), n)
        self.assertEqual(int(muestra.dentro.sum()), dentro)


class PruebasValidacion(unittest.TestCase):
    """Validación: el estimador debe comportarse como predice la teoría."""

    def test_estimacion_cercana_a_pi(self):
        resultado = ExperimentoMonteCarlo(PARAMETROS_NUMERICAL_RECIPES, EstimadorPiMonteCarlo()).ejecutar(100_000)
        # Error estándar con N=100 000 ≈ 0.0052; se acepta hasta 4 errores estándar.
        self.assertLess(resultado.error_absoluto, 4 * 4 * math.sqrt((math.pi / 4) * (1 - math.pi / 4) / 100_000))

    def test_dispersion_coincide_con_la_teoria(self):
        # Con semillas independientes la desviación de π̂ debe parecerse a 4·sqrt(p(1-p)/N) ≈ 0.052 (N=1000).
        experimento = ExperimentoMonteCarlo(PARAMETROS_NUMERICAL_RECIPES, EstimadorPiMonteCarlo())
        resumen = experimento.repetir(1_000, experimento.semillas_repeticiones(30))
        teorica = 4 * math.sqrt((math.pi / 4) * (1 - math.pi / 4) / 1_000)
        self.assertTrue(0.5 * teorica < resumen.desviacion_pi < 2 * teorica)

    def test_error_medio_disminuye_con_n(self):
        experimento = ExperimentoMonteCarlo(PARAMETROS_NUMERICAL_RECIPES, EstimadorPiMonteCarlo())
        semillas = experimento.semillas_repeticiones(10)
        error_pequenio = experimento.repetir(1_000, semillas).error_promedio
        error_grande = experimento.repetir(100_000, semillas).error_promedio
        self.assertLess(error_grande, error_pequenio)


if __name__ == "__main__":
    unittest.main()
