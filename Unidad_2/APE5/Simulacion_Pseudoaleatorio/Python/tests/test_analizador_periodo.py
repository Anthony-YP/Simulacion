"""Pruebas del análisis del período (Hull-Dobell, Brent y búsqueda en la muestra)."""

import unittest

from lcg.modelo import AnalizadorPeriodo, GeneradorCongruencialLineal, ParametrosLCG

PRACTICA = ParametrosLCG(a=1_664_525, c=1_013_904_223, m=2**32, semilla=12_345)


class PruebasHullDobell(unittest.TestCase):
    def setUp(self):
        self.analizador = AnalizadorPeriodo()

    def test_parametros_de_la_practica_tienen_periodo_completo(self):
        resultado = self.analizador.verificar_hull_dobell(PRACTICA)
        self.assertEqual(resultado.factores_primos_m, (2,))
        self.assertEqual(resultado.mcd_c_m, 1)
        self.assertTrue(resultado.periodo_completo)

    def test_cada_condicion_por_separado(self):
        # (a, c, m) -> (condición 1, condición 2, condición 3)
        casos = {
            (5, 3, 16): (True, True, True),
            (5, 2, 16): (False, True, True),   # c par
            (3, 3, 16): (True, True, False),   # a - 1 = 2 no es múltiplo de 4
            (4, 3, 16): (True, False, False),  # a par: a - 1 impar
            (6, 1, 9): (True, False, True),    # 9 no es múltiplo de 4: la condición 3 no aplica
        }
        for (a, c, m), esperado in casos.items():
            with self.subTest(a=a, c=c, m=m):
                r = self.analizador.verificar_hull_dobell(ParametrosLCG(a, c, m, 7))
                self.assertEqual(
                    (r.c_coprimo_con_m, r.a_menos_1_divisible_por_primos, r.a_menos_1_multiplo_de_4), esperado)

    def test_factores_primos(self):
        casos = {2**32: (2,), 1000: (2, 5), 97: (97,), 2 * 3 * 7 * 7: (2, 3, 7), 2: (2,)}
        for m, esperado in casos.items():
            with self.subTest(m=m):
                self.assertEqual(AnalizadorPeriodo._factores_primos(m), esperado)


class PruebasCiclo(unittest.TestCase):
    def setUp(self):
        self.analizador = AnalizadorPeriodo()

    def medir(self, parametros, limite=None):
        generador = GeneradorCongruencialLineal(parametros)
        return self.analizador.medir_periodo(generador.transicion, parametros.semilla, limite)

    def test_brent_en_los_escenarios_de_la_practica(self):
        # (a, c, m, semilla) -> (lambda, mu)
        casos = {
            (5, 3, 16, 7): (16, 0),
            (5, 2, 16, 7): (8, 0),
            (3, 3, 16, 7): (8, 0),
            (4, 3, 16, 7): (1, 1),
            (1_664_524, 1_013_904_223, 2**32, 12_345): (1, 16),
        }
        for (a, c, m, semilla), (periodo, inicio) in casos.items():
            with self.subTest(a=a, c=c, m=m):
                resultado = self.medir(ParametrosLCG(a, c, m, semilla))
                self.assertTrue(resultado.encontrado)
                self.assertEqual((resultado.periodo, resultado.inicio_ciclo), (periodo, inicio))

    def test_brent_coincide_con_la_busqueda_directa_y_con_hull_dobell(self):
        # Validación exhaustiva con m = 32: para todo a y c, Brent y la búsqueda con
        # diccionario dan el mismo ciclo, y el período es m si y solo si se cumple Hull-Dobell.
        m = 32
        for a in range(1, m):
            for c in range(m):
                parametros = ParametrosLCG(a, c, m, semilla=7)
                brent = self.medir(parametros)
                directo = self.analizador.buscar_repeticion(
                    7, GeneradorCongruencialLineal(parametros).generar(m + 1))
                teoria = self.analizador.verificar_hull_dobell(parametros)
                with self.subTest(a=a, c=c):
                    self.assertEqual((brent.periodo, brent.inicio_ciclo), (directo.periodo, directo.inicio_ciclo))
                    self.assertEqual(teoria.periodo_completo, brent.periodo == m)

    def test_mismos_a_y_c_tienen_periodo_completo_en_modulos_menores(self):
        # Reducir a y c módulo 2^k conserva las condiciones de Hull-Dobell, así que el
        # período medido debe ser exactamente 2^k: evidencia empírica a favor de 2^32.
        for k in range(2, 19):
            m = 2**k
            with self.subTest(m=m):
                resultado = self.medir(ParametrosLCG(PRACTICA.a % m, PRACTICA.c % m, m, PRACTICA.semilla % m))
                self.assertEqual((resultado.periodo, resultado.inicio_ciclo), (m, 0))

    def test_respeta_el_limite_de_pasos(self):
        resultado = self.medir(PRACTICA, limite=1000)
        self.assertFalse(resultado.encontrado)
        self.assertEqual(resultado.pasos, 1000)

    def test_sin_repeticiones_en_la_muestra_de_la_practica(self):
        muestra = GeneradorCongruencialLineal(PRACTICA).generar(10_000)
        resultado = self.analizador.buscar_repeticion(PRACTICA.semilla, muestra)
        self.assertFalse(resultado.encontrado)
        self.assertEqual(resultado.pasos, 10_000)


if __name__ == "__main__":
    unittest.main()
