import pytest

from src.teoria import es_estable, metricas_teoricas


def test_es_estable_cuando_llegadas_menores_que_servicio():
    assert es_estable(2.0, 3.0) is True


def test_no_es_estable_cuando_llegadas_igualan_o_superan_servicio():
    assert es_estable(3.0, 3.0) is False
    assert es_estable(3.5, 3.0) is False


def test_escenario_1():
    m = metricas_teoricas(2.0, 3.0)
    assert m["rho"] == pytest.approx(0.6667, abs=1e-3)
    assert m["L"] == pytest.approx(2.0)
    assert m["Lq"] == pytest.approx(1.3333, abs=1e-3)
    assert m["W"] == pytest.approx(1.0)
    assert m["Wq"] == pytest.approx(0.6667, abs=1e-3)


def test_escenario_2():
    m = metricas_teoricas(2.5, 3.0)
    assert m["rho"] == pytest.approx(0.8333, abs=1e-3)
    assert m["L"] == pytest.approx(5.0)
    assert m["Lq"] == pytest.approx(4.1667, abs=1e-3)
    assert m["W"] == pytest.approx(2.0)
    assert m["Wq"] == pytest.approx(1.6667, abs=1e-3)


def test_escenario_3_cerca_de_saturacion():
    m = metricas_teoricas(2.9, 3.0)
    assert m["rho"] == pytest.approx(0.9667, abs=1e-3)
    assert m["L"] == pytest.approx(29.0)
    assert m["Lq"] == pytest.approx(28.0333, abs=1e-3)
    assert m["W"] == pytest.approx(10.0)
    assert m["Wq"] == pytest.approx(9.6667, abs=1e-3)


def test_sistema_inestable_lanza_error():
    with pytest.raises(ValueError, match="El sistema no es estable"):
        metricas_teoricas(3.0, 3.0)
