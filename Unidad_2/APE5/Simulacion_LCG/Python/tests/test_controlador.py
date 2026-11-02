"""Prueba de integración: el controlador ejecuta los 8 pasos con dependencias reales."""

import io
import tempfile
import unittest
from pathlib import Path

from lcg.controlador import ConfiguracionSimulacion, ControladorSimulacion
from lcg.modelo import (
    AnalizadorEstadistico,
    AnalizadorPeriodo,
    ComparadorSecuencias,
    GeneradorCongruencialLineal,
    ParametrosLCG,
    RepositorioCSV,
)
from lcg.vista import VistaConsola

PRACTICA = ParametrosLCG(a=1_664_525, c=1_013_904_223, m=2**32, semilla=12_345)


class PruebasControlador(unittest.TestCase):
    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.raiz = Path(self.carpeta.name)

    def tearDown(self):
        self.carpeta.cleanup()

    def ejecutar(self, directorio_externo):
        salida = io.StringIO()
        configuracion = ConfiguracionSimulacion(
            parametros=PRACTICA,
            cantidad=500,
            directorio_resultados=self.raiz / "python",
            directorio_externo=directorio_externo,
        )
        ControladorSimulacion(
            configuracion, GeneradorCongruencialLineal, AnalizadorPeriodo(), AnalizadorEstadistico(),
            ComparadorSecuencias(), RepositorioCSV(), VistaConsola(salida),
        ).ejecutar()
        return salida.getvalue()

    def test_ejecuta_todos_los_pasos_sin_otra_implementacion(self):
        texto = self.ejecutar(directorio_externo=None)
        for paso in ("Paso 1.", "Pasos 2 y 3.", "Paso 4.", "Paso 5.", "Paso 6.", "Paso 7.", "Paso 8."):
            self.assertIn(paso, texto)
        for semilla in (12_345, 54_321):
            self.assertTrue((self.raiz / "python" / f"secuencia_python_semilla_{semilla}.csv").is_file())

    def test_compara_con_los_csv_de_la_otra_implementacion(self):
        # Simula la carpeta de resultados de Java con archivos generados por el mismo algoritmo.
        carpeta_java = self.raiz / "java"
        for semilla in (12_345, 54_321):
            RepositorioCSV().guardar(
                GeneradorCongruencialLineal(PRACTICA.con_semilla(semilla)).generar(500),
                carpeta_java / f"secuencia_java_semilla_{semilla}.csv",
            )
        texto = self.ejecutar(directorio_externo=carpeta_java)
        self.assertEqual(texto.count("Veredicto: las secuencias son IDÉNTICAS."), 2)
        self.assertTrue((self.raiz / "python" / "comparacion_python_java_semilla_12345.csv").is_file())


if __name__ == "__main__":
    unittest.main()
