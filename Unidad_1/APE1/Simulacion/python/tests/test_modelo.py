"""Etapa 5 - Verificación: el modelo calcula lo que dice la guía."""

import unittest

import numpy as np

from model import clima, exponencial


class TestClima(unittest.TestCase):

    def test_ejemplo_de_la_guia(self):
        # Humedad 90 %, nubosidad 80 %, 18 °C -> I = 0.81 -> Lluvia
        tf = clima.factor_temperatura(18)
        i = clima.indice_lluvia(0.90, 0.80, tf, clima.MODELO_ORIGINAL)
        self.assertAlmostEqual(tf, 0.60)
        self.assertAlmostEqual(i, 0.81)
        self.assertEqual(clima.clasificar(i), "Lluvia")

    def test_factor_temperatura_coincide_con_tabla(self):
        tabla = {10: 1.0, 12: 0.9, 14: 0.8, 16: 0.7, 18: 0.6,
                 20: 0.5, 22: 0.4, 24: 0.3, 26: 0.2, 28: 0.1}
        for t, tf in tabla.items():
            self.assertAlmostEqual(clima.factor_temperatura(t), tf)
        self.assertEqual(clima.factor_temperatura(5), 1.0)   # ≤ 10 °C
        self.assertEqual(clima.factor_temperatura(35), 0.1)  # ≥ 28 °C

    def test_limites_de_clasificacion(self):
        self.assertEqual(clima.clasificar(0.39), "Sin lluvia")
        self.assertEqual(clima.clasificar(0.40), "Baja posibilidad")
        self.assertEqual(clima.clasificar(0.60), "Lluvia probable")
        self.assertEqual(clima.clasificar(0.75), "Lluvia")

    def test_pesos_invalidos(self):
        with self.assertRaises(ValueError):
            clima.PesosModelo("malo", 0.5, 0.5, 0.5)


class TestExponencial(unittest.TestCase):

    def test_p0_y_signo_de_r(self):
        t = np.array([0.0, 10.0])
        self.assertEqual(exponencial.poblacion(t, 100, 0.1)[0], 100)  # P(0) = P0
        self.assertGreater(exponencial.poblacion(t, 100, 0.1)[1], 100)
        self.assertLess(exponencial.poblacion(t, 100, -0.1)[1], 100)


if __name__ == "__main__":
    unittest.main()
