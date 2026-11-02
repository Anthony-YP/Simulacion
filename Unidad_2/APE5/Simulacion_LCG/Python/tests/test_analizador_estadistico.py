"""Pruebas de los estadísticos de uniformidad e independencia."""

import unittest
from math import sqrt

from lcg.modelo import AnalizadorEstadistico, GeneradorCongruencialLineal, Observacion, ParametrosLCG

PRACTICA = ParametrosLCG(a=1_664_525, c=1_013_904_223, m=2**32, semilla=12_345)


def muestra(valores):
    """Construye observaciones a partir de valores U (X no interviene en la estadística)."""
    return [Observacion(n, 0, u) for n, u in enumerate(valores, start=1)]


class PruebasAnalizadorEstadistico(unittest.TestCase):
    def setUp(self):
        self.analizador = AnalizadorEstadistico()

    def test_muestra_perfectamente_uniforme(self):
        resumen = self.analizador.analizar(muestra((i + 0.5) / 10 for i in range(10)))
        self.assertEqual(resumen.frecuencias, (1,) * 10)
        self.assertAlmostEqual(resumen.media, 0.5)
        self.assertEqual(resumen.chi_cuadrado, 0.0)
        self.assertTrue(resumen.pasa_chi_cuadrado)

    def test_muestra_concentrada_rechaza_la_uniformidad(self):
        resumen = self.analizador.analizar(muestra([0.05] * 99 + [0.95]))
        self.assertEqual(resumen.frecuencias[0], 99)
        self.assertFalse(resumen.pasa_chi_cuadrado)

    def test_autocorrelacion_de_una_secuencia_alternante(self):
        # Desviaciones +-0.25 alternadas: 99 productos de -0.0625 sobre 100 cuadrados de 0.0625.
        resumen = self.analizador.analizar(muestra([0.25, 0.75] * 50))
        self.assertAlmostEqual(resumen.autocorrelacion_lag1, -0.99)

    def test_secuencia_de_la_practica_se_comporta_como_uniforme(self):
        resumen = self.analizador.analizar(GeneradorCongruencialLineal(PRACTICA).generar(10_000))
        self.assertEqual(sum(resumen.frecuencias), 10_000)
        self.assertAlmostEqual(resumen.media, 0.5, delta=0.01)
        self.assertAlmostEqual(resumen.varianza, 1 / 12, delta=0.005)
        self.assertTrue(resumen.pasa_chi_cuadrado)
        # Banda de 95 % para la autocorrelación de una muestra independiente: +-1.96/sqrt(N).
        self.assertLess(abs(resumen.autocorrelacion_lag1), 1.96 / sqrt(10_000))

    def test_requiere_al_menos_dos_valores(self):
        with self.assertRaises(ValueError):
            self.analizador.analizar(muestra([0.5]))


if __name__ == "__main__":
    unittest.main()
