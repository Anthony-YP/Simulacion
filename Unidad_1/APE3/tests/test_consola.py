import io
import re

from rich.console import Console

from src.consola import (
    barra_utilizacion,
    color_error,
    color_utilizacion,
    esperar_enter,
    mostrar_escenario,
    mostrar_inestable,
    mostrar_menu,
    mostrar_resumen_escenarios,
    mostrar_tabla,
    pedir_opcion,
)

ESCENARIO = {"escenario": 3, "lam": 2.9, "mu": 3.0, "condicion": "Cerca de saturacion"}
RESULTADO = {
    "escenario": 3,
    "lam": 2.9,
    "mu": 3.0,
    "rho": 0.9667,
    "L": 29.0,
    "Lq": 28.0333,
    "W": 10.0,
    "Wq": 9.6667,
    "espera_promedio": 8.2279,
    "cola_promedio": 23.7584,
    "clientes_atendidos": 28950,
    "error_Wq_%": 14.884,
    "error_Lq_%": 15.249,
}


def consola_de_prueba():
    return Console(record=True, width=140, color_system=None)


def test_color_error_por_rango():
    assert color_error(5.0) == "green"
    assert color_error(14.9) == "yellow"
    assert color_error(25.0) == "red"


def test_color_utilizacion_por_rango():
    assert color_utilizacion(0.79) == "green"
    assert color_utilizacion(0.8) == "yellow"
    assert color_utilizacion(0.95) == "red"


def test_barra_utilizacion_usa_el_color_de_rho():
    barra = barra_utilizacion(0.9667, ancho=10)
    assert "96.7%" in barra.plain
    assert barra.style == "red"


def test_escenario_muestra_teorico_y_simulado():
    consola = consola_de_prueba()
    mostrar_escenario(ESCENARIO, RESULTADO, consola)
    texto = consola.export_text()
    assert "Escenario 3" in texto
    assert "9.667" in texto
    assert "8.228" in texto
    assert "28,950" in texto


def test_tabla_muestra_todas_las_metricas():
    consola = consola_de_prueba()
    mostrar_tabla([RESULTADO], consola)
    texto = consola.export_text()
    for valor in ["0.967", "29.000", "28.033", "10.000", "9.667", "8.228", "23.758", "14.9%", "15.2%"]:
        assert valor in texto


def test_inestable_avisa_al_usuario():
    consola = consola_de_prueba()
    mostrar_inestable(4, 3.5, 3.0, consola)
    assert "no es estable" in consola.export_text()


ESCENARIOS = [
    {"escenario": 1, "lam": 2.0, "mu": 3.0, "condicion": "Sistema estable"},
    ESCENARIO,
]


def test_menu_lista_escenarios_todos_y_salir():
    consola = consola_de_prueba()
    mostrar_menu(ESCENARIOS, 10000, 42, consola)
    texto = consola.export_text()
    assert "M/M/1" in texto
    assert "Escenario 1 · Sistema estable" in texto
    assert "Cerca de saturacion" in texto
    assert "0.667" in texto
    # La opción "todos" es n + 1 (aquí 3), no un 4 fijo
    assert re.search(r"3\s+Todos los escenarios", texto)
    assert "Salir" in texto
    assert "10000" in texto
    assert "42" in texto


def test_esperar_enter_muestra_el_aviso_y_continua():
    consola = consola_de_prueba()
    esperar_enter(consola, stream=io.StringIO("\n"))
    assert "Presiona Enter para volver al menú" in consola.export_text()


def test_resumen_muestra_un_panel_por_escenario():
    esc_1 = {"escenario": 1, "lam": 2.0, "mu": 3.0, "condicion": "Sistema estable"}
    res_1 = {
        **RESULTADO,
        "escenario": 1,
        "lam": 2.0,
        "rho": 0.6667,
        "Wq": 0.6667,
        "espera_promedio": 0.6512,
        "Lq": 1.3333,
        "cola_promedio": 1.3021,
        "clientes_atendidos": 19980,
        "error_Wq_%": 2.325,
        "error_Lq_%": 2.34,
    }
    consola = consola_de_prueba()
    mostrar_resumen_escenarios([(esc_1, res_1), (ESCENARIO, RESULTADO)], consola)
    texto = consola.export_text()
    assert "Escenario 1" in texto
    assert "Escenario 3" in texto
    assert "Sistema estable" in texto
    assert "19,980" in texto
    assert "28,950" in texto
    assert "0.651" in texto
    assert "8.228" in texto
    assert "14.9%" in texto


def test_pedir_opcion_devuelve_numero_elegido():
    consola = consola_de_prueba()
    assert pedir_opcion(ESCENARIOS, consola, stream=io.StringIO("2\n")) == 2


def test_pedir_opcion_vuelve_a_preguntar_si_la_opcion_no_existe():
    consola = consola_de_prueba()
    opcion = pedir_opcion(ESCENARIOS, consola, stream=io.StringIO("9\nabc\n0\n"))
    assert opcion == 0


def test_pedir_opcion_avisa_en_espanol_si_la_opcion_no_existe():
    consola = consola_de_prueba()
    pedir_opcion(ESCENARIOS, consola, stream=io.StringIO("9\n0\n"))
    assert "Opción no válida" in consola.export_text()
