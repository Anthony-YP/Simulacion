"""Capa Vista: presenta los datos del modelo; no contiene lógica del dominio.

VistaGraficosMatplotlib no se importa aquí para que la consola funcione aunque
matplotlib no esté instalado; se importa desde lcg.vista.vista_graficos.
"""

from .contratos import VistaGraficos, VistaResultados
from .vista_consola import VistaConsola

__all__ = ["VistaConsola", "VistaGraficos", "VistaResultados"]
