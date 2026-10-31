# Modelo SIR con Python y SimPy

Práctica 04 de Simulación (UNL, Computación, ciclo 5): análisis comparativo de herramientas de simulación mediante un modelo común.

El programa simula la propagación de una infección en una población de 100 personas con el modelo SIR y genera:

- **`resultados_python.csv`**: los datos que se importan en NetLogo.
- **`grafica_sir_python.png`**: la gráfica de S(t), I(t) y R(t).
- **`reporte_python.html`**: un reporte ilustrado que explica la práctica.

## Inicio rápido

```bash
cd python
pip install -r requirements.txt
python main.py
```

Los tres archivos se crean en la carpeta desde la que se ejecuta el programa, y el reporte se abre en el navegador. Para no abrirlo, se agrega `--sin-navegador`.

Sin instalar dependencias en el sistema, con [uv](https://docs.astral.sh/uv/):

```bash
cd python
uv run --no-project --with simpy --with matplotlib python main.py
```

Salida esperada:

```
Simulación SIR finalizada correctamente.
Archivos creados: resultados_python.csv, grafica_sir_python.png y reporte_python.html
Tiempo final: 100 | Susceptibles: 2 | Infectados: 0 | Recuperados: 98
```

## Parámetros comunes

Son los mismos en Python y en NetLogo y no deben cambiarse.

| Parámetro | Valor |
|-----------|-------|
| Población | 100 |
| Infectados iniciales | 5 |
| β (tasa de infección) | 0.30 |
| γ (tasa de recuperación) | 0.10 |
| Tiempo | 0 a 100 |
| Semilla | 42 |

## Cómo funciona cada paso

1. Se registran el tiempo y los conteos de S, I y R.
2. Se toma una copia del estado de la población.
3. Cada infectado elige un contacto al azar. Si es susceptible y `random < β`, se contagia.
4. Cada infectado se recupera si `random < γ`.
5. SimPy avanza el reloj una unidad (`env.timeout(1)`).

Los cambios se calculan sobre la copia, de modo que nadie contagiado en un paso contagia en ese mismo paso.

## Estructura

El proyecto sigue el patrón Modelo-Vista-Controlador.

| Archivo | Responsabilidad |
|---------|-----------------|
| `python/model.py` | Parte 1 (estados, parámetros, población) y Parte 2 (simulación con SimPy) |
| `python/view.py` | Parte 3: CSV, gráfica y reporte HTML |
| `python/controller.py` | Parte 4: ejecuta el modelo y entrega los resultados a las vistas |
| `python/main.py` | Programa principal |
| `python/test_model.py` | Pruebas del modelo y del controlador |
| `python/test_view.py` | Pruebas del CSV, la gráfica y el reporte |

## Pruebas

```bash
cd python
python -m unittest -v
```

Las 13 pruebas verifican, entre otras cosas:

- 101 registros.
- Primera fila 95/5/0.
- S + I + R = 100 en cada instante.
- La misma semilla da el mismo resultado.
- Con β = 0 no hay contagios.

## Integración con NetLogo

1. Ejecutar `python main.py`.
2. Copiar `resultados_python.csv` a la carpeta de `modelo_sir_netlogo.nlogo`.
3. En NetLogo, usar el botón **CARGAR PYTHON** para importar y graficar los datos.

El CSV usa la cabecera `tiempo,susceptibles,infectados,recuperados` y tiene 101 filas de datos.
