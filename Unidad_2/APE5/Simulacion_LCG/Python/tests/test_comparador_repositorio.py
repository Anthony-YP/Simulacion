"""Pruebas del comparador de secuencias y del formato CSV compartido con Java."""

import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from lcg.modelo import ComparadorSecuencias, GeneradorCongruencialLineal, Observacion, ParametrosLCG, RepositorioCSV

PRACTICA = ParametrosLCG(a=1_664_525, c=1_013_904_223, m=2**32, semilla=12_345)


def generar(cantidad, semilla=12_345):
    return GeneradorCongruencialLineal(PRACTICA.con_semilla(semilla)).generar(cantidad)


class PruebasComparador(unittest.TestCase):
    def setUp(self):
        self.comparador = ComparadorSecuencias()

    def test_secuencias_identicas(self):
        resultado = self.comparador.comparar(generar(100), generar(100))
        self.assertTrue(resultado.identicas)
        self.assertEqual(resultado.coincidencias, 100)
        self.assertIsNone(resultado.primera_discrepancia)
        self.assertEqual(resultado.diferencia_maxima_u, 0.0)

    def test_detecta_la_primera_diferencia(self):
        a = generar(10)
        b = list(a)
        b[4] = replace(b[4], x=b[4].x + 1)
        resultado = self.comparador.comparar(a, b)
        self.assertFalse(resultado.identicas)
        self.assertEqual(resultado.primera_discrepancia, 5)

    def test_longitudes_distintas_no_son_identicas(self):
        a = generar(10)
        resultado = self.comparador.comparar(a, a[:8])
        self.assertEqual((resultado.comparadas, resultado.coincidencias), (8, 8))
        self.assertFalse(resultado.identicas)

    def test_semillas_distintas_no_coinciden(self):
        resultado = self.comparador.comparar(generar(1000), generar(1000, semilla=54_321))
        self.assertEqual(resultado.coincidencias, 0)


class PruebasRepositorioCSV(unittest.TestCase):
    def setUp(self):
        self.repositorio = RepositorioCSV()
        self.carpeta = tempfile.TemporaryDirectory()
        self.ruta = Path(self.carpeta.name) / "secuencia.csv"

    def tearDown(self):
        self.carpeta.cleanup()

    def test_formato_exacto_del_archivo(self):
        self.repositorio.guardar(generar(2), self.ruta)
        self.assertEqual(
            self.ruta.read_bytes(),
            b"n,X_n,U_n\n1,87628868,0.0204026857\n2,71072467,0.0165478482\n",
        )

    def test_ida_y_vuelta(self):
        originales = generar(500)
        self.repositorio.guardar(originales, self.ruta)
        cargadas = self.repositorio.cargar(self.ruta)
        self.assertEqual([(o.n, o.x) for o in cargadas], [(o.n, o.x) for o in originales])
        for original, cargada in zip(originales, cargadas):
            self.assertAlmostEqual(original.u, cargada.u, delta=5e-11)  # error máximo por redondear a 10 decimales

    def test_empate_se_redondea_al_par(self):
        # U = 2^21 / 2^32 = 0.00048828125 es un empate exacto en el 11.o decimal.
        # Redondeo al par: ...812|5 -> ...812 (el redondeo "hacia arriba" daría ...813).
        self.repositorio.guardar([Observacion(1, 2**21, 2**21 / 2**32)], self.ruta)
        self.assertEqual(self.ruta.read_text().splitlines()[1], "1,2097152,0.0004882812")

    def test_rechaza_un_encabezado_desconocido(self):
        self.ruta.write_text("a,b,c\n1,2,3\n")
        with self.assertRaises(ValueError):
            self.repositorio.cargar(self.ruta)


if __name__ == "__main__":
    unittest.main()
