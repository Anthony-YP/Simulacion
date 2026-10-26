"""CONTROLADOR - Une el Modelo con la Vista.

Pide los cálculos al modelo y envía los resultados a la vista.
Etapas cubiertas: 6. Experimentación (original vs. ajustado, varios r)
y 7. Documentación (tablas CSV y gráficas en resultados/).
"""

from pathlib import Path

from model import clima, exponencial
from view import consola, graficas


class SimulacionController:

    def __init__(self, carpeta_salida: Path) -> None:
        self.salida = carpeta_salida

    def ejecutar(self) -> None:
        # PASO 1 - Preparar la carpeta donde se guardan los resultados
        self.salida.mkdir(parents=True, exist_ok=True)

        # PASO 2 - Simular con el modelo original y con el ajustado
        original = clima.simular(clima.DATOS_GUIA, clima.MODELO_ORIGINAL)
        ajustado = clima.simular(clima.DATOS_GUIA, clima.MODELO_AJUSTADO)

        # PASO 3 - Mostrar y guardar las tablas que pide la guía
        consola.mostrar_tabla("Modelo original: I = 0.5H + 0.3N + 0.2Tf", original)
        consola.mostrar_tabla("Modelo ajustado: I = 0.45H + 0.40N + 0.15Tf", ajustado)
        print()
        consola.mostrar_horas_lluvia("Original", original)
        consola.mostrar_horas_lluvia("Ajustado", ajustado)
        consola.guardar_csv(original, self.salida / "tabla_original.csv")
        consola.guardar_csv(ajustado, self.salida / "tabla_ajustada.csv")

        # PASO 4 - Gráficas del índice de lluvia
        for nombre, res in (("original", original), ("ajustado", ajustado)):
            graficas.grafica_indice(f"Índice de lluvia - modelo {nombre}", res,
                                    self.salida / f"indice_{nombre}.png")
        graficas.grafica_variables(original, self.salida / "variables.png")
        graficas.grafica_comparacion(original, ajustado, self.salida / "comparacion.png")

        # PASO 5 - Modelo exponencial: influencia de r
        curvas = exponencial.simular_tasas()
        info = [(r, float(p[-1]), exponencial.tiempo_duplicacion_o_vida_media(r))
                for r, p in curvas.items()]
        consola.mostrar_tasas(info)
        graficas.grafica_exponencial(exponencial.TIEMPO, curvas,
                                     self.salida / "exponencial.png")

        print(f"\nResultados guardados en: {self.salida.resolve()}")
