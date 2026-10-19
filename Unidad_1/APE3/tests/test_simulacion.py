
import pytest

from src.simulacion import simular


def test_simulacion_retorna_las_metricas_esperadas():
    resultados = simular(
        lam=2.0,
        mu=3.0,
        tiempo_simulacion=100,
        semilla=42,
    )

    assert resultados["clientes_llegados"] > 0
    assert resultados["clientes_atendidos"] >= 0
    assert resultados["clientes_pendientes"] >= 0
    assert resultados["clientes_atendidos"] <= resultados["clientes_llegados"]

    assert resultados["Wq_simulado"] >= 0
    assert resultados["W_simulado"] >= 0
    assert resultados["cola_promedio_en_llegadas"] >= 0


def test_simulacion_es_reproducible_con_la_misma_semilla():
    resultado_1 = simular(2.0, 3.0, 100, semilla=42)
    resultado_2 = simular(2.0, 3.0, 100, semilla=42)

    assert resultado_1 == resultado_2


def test_muestras_cola_registran_llegadas_e_inicios_de_servicio():
    resultados = simular(2.0, 3.0, 100, semilla=42)

    # One sample when each customer arrives and another when service starts.
    esperados = resultados["clientes_llegados"] + len(resultados["tiempos_espera"])
    assert len(resultados["muestras_cola"]) == esperados


def test_sistema_inestable_lanza_error():
    with pytest.raises(ValueError, match="El sistema no es estable"):
        simular(3.0, 3.0, 100)


def test_tasas_no_positivas_lanzan_error():
    with pytest.raises(ValueError, match="Las tasas deben ser mayores que cero"):
        simular(0, 3.0, 100)

    with pytest.raises(ValueError, match="Las tasas deben ser mayores que cero"):
        simular(2.0, -1.0, 100)


def test_tiempo_de_simulacion_no_positivo_lanza_error():
    with pytest.raises(
        ValueError,
        match="El tiempo de simulacion debe ser positivo",
    ):
        simular(2.0, 3.0, 0)


def test_escenarios_de_opcion_uno_o_todos():
    from src.experimentos import ESCENARIOS, escenarios_de_opcion

    assert escenarios_de_opcion(2) == [ESCENARIOS[1]]
    assert escenarios_de_opcion(len(ESCENARIOS) + 1) == ESCENARIOS
