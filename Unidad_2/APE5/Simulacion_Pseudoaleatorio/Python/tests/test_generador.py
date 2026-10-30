"""Pruebas del generador y de sus parámetros."""

import unittest

from lcg.modelo import GeneradorCongruencialLineal, ParametrosLCG

PRACTICA = ParametrosLCG(a=1_664_525, c=1_013_904_223, m=2**32, semilla=12_345)


class PruebasParametros(unittest.TestCase):
    def test_rechaza_parametros_fuera_de_rango(self):
        casos = [
            dict(a=5, c=3, m=1, semilla=0),   # m < 2
            dict(a=0, c=3, m=16, semilla=7),  # a <= 0
            dict(a=16, c=3, m=16, semilla=7),  # a >= m
            dict(a=5, c=-1, m=16, semilla=7),  # c < 0
            dict(a=5, c=16, m=16, semilla=7),  # c >= m
            dict(a=5, c=3, m=16, semilla=-1),  # semilla < 0
            dict(a=5, c=3, m=16, semilla=16),  # semilla >= m
        ]
        for caso in casos:
            with self.subTest(**caso), self.assertRaises(ValueError):
                ParametrosLCG(**caso)

    def test_rechaza_valores_que_desbordarian_un_long_de_java(self):
        with self.assertRaises(ValueError):
            ParametrosLCG(a=2**32 - 1, c=0, m=2**32, semilla=1)

    def test_con_semilla_solo_cambia_la_semilla(self):
        nuevos = PRACTICA.con_semilla(54_321)
        self.assertEqual((nuevos.a, nuevos.c, nuevos.m, nuevos.semilla), (PRACTICA.a, PRACTICA.c, PRACTICA.m, 54_321))
        self.assertEqual(PRACTICA.semilla, 12_345)  # el objeto original es inmutable


class PruebasGenerador(unittest.TestCase):
    def test_primer_valor_calculado_a_mano(self):
        # (1664525 * 12345 + 1013904223) mod 2^32 = 21562465348 mod 4294967296 = 87628868
        obs = GeneradorCongruencialLineal(PRACTICA).siguiente()
        self.assertEqual((obs.n, obs.x), (1, 87_628_868))
        self.assertEqual(obs.u, 87_628_868 / 2**32)

    def test_coincide_con_la_secuencia_publicada_en_numerical_recipes(self):
        # Numerical Recipes in C (2.a ed., sección 7.1) publica estos valores, en
        # hexadecimal, para el generador a = 1664525, c = 1013904223, m = 2^32 con semilla 0.
        publicados = [0x3C6EF35F, 0x47502932, 0xD1CCF6E9, 0xAAF95334, 0x6252E503, 0x9F2EC686,
                      0x57FE6C2D, 0xA3D95FA8, 0x81FDBEE7, 0x94F0AF1A, 0xCBF633B1]
        generador = GeneradorCongruencialLineal(PRACTICA.con_semilla(0))
        self.assertEqual([obs.x for obs in generador.generar(len(publicados))], publicados)

    def test_misma_semilla_misma_secuencia(self):
        self.assertEqual(GeneradorCongruencialLineal(PRACTICA).generar(1000),
                         GeneradorCongruencialLineal(PRACTICA).generar(1000))

    def test_reiniciar_reproduce_la_secuencia(self):
        generador = GeneradorCongruencialLineal(PRACTICA)
        primera = generador.generar(50)
        generador.reiniciar()
        self.assertEqual(generador.generar(50), primera)

    def test_valores_normalizados_en_el_intervalo_unitario(self):
        for obs in GeneradorCongruencialLineal(PRACTICA).generar(10_000):
            self.assertTrue(0 <= obs.u < 1)
            self.assertEqual(obs.u, obs.x / PRACTICA.m)

    def test_cantidad_cero_y_negativa(self):
        generador = GeneradorCongruencialLineal(PRACTICA)
        self.assertEqual(generador.generar(0), [])
        with self.assertRaises(ValueError):
            generador.generar(-1)

    def test_transicion_no_altera_el_estado(self):
        generador = GeneradorCongruencialLineal(PRACTICA)
        generador.transicion(999)
        self.assertEqual(generador.siguiente().x, 87_628_868)


if __name__ == "__main__":
    unittest.main()
