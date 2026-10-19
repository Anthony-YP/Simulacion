# Práctica 3: cola M/M/1

Proyecto de Simulación que estudia una cola M/M/1 con un servidor. En cada
escenario genera llegadas y servicios aleatorios, calcula las métricas teóricas
y compara estas con los resultados observados en la simulación. Así se puede
ver cómo aumenta la espera y la longitud de la cola al acercarse la tasa de
llegada a la capacidad del servidor.

## Tecnologías

- Python
- SimPy: simulación de eventos discretos
- NumPy: números aleatorios y cálculos
- Matplotlib: gráficas
- pytest: pruebas

## Instalación y ejecución

Se requiere Python 3.9 o posterior. Desde la carpeta del proyecto:

```bash
python -m venv .venv
```

Activar el entorno:

```bash
# Linux o macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Instalar dependencias y ejecutar:

```bash
python -m pip install -r requirements.txt
python main.py
```

Al iniciar se muestra un menú: las opciones `1`, `2` y `3` simulan un solo
escenario, `4` simula los tres y genera la comparación, y `0` sale del
programa. Después de cada simulación se presiona Enter para volver al menú,
que se repite hasta elegir `0`.

## Resultados

El programa guarda en `resultados/`:

- `cola_esc1.png`, `cola_esc2.png`, `cola_esc3.png`: número de clientes en
  espera a lo largo del tiempo simulado (se muestra hasta el tiempo 200).
- `esperas_esc1.png`, `esperas_esc2.png`, `esperas_esc3.png`: distribución de
  los tiempos de espera de los clientes; la línea roja indica el promedio.
- `comparacion.png`: compara el tiempo promedio en cola (`Wq`) y el promedio
  de clientes en cola (`Lq`) teóricos y simulados para los tres escenarios.
- `tabla.csv`: datos numéricos de los escenarios, incluyendo utilización
  (`rho`), métricas teóricas y simuladas y errores porcentuales de `Wq` y `Lq`.

En las métricas M/M/1, `L` y `Lq` representan promedios de clientes en el
sistema y en la cola; `W` y `Wq` son los tiempos promedio correspondientes.
El promedio simulado de clientes en cola se estima observando la cola cuando
llegan clientes.

Para correr las pruebas:

```bash
python -m pytest -q
```

## Estructura

```text
src/
  teoria.py       # Estabilidad y métricas teóricas
  simulacion.py   # Simulación M/M/1
  graficas.py     # Gráficas de cola, esperas y comparación
  experimentos.py # Escenarios y tabla comparativa
tests/            # Pruebas de teoría y simulación
main.py           # Ejecución del proyecto
resultados/       # Imágenes y tabla generadas
```

## Escenarios

La simulación dura `10000` unidades de tiempo y usa la semilla `42`.

| Escenario | `lambda` | `mu` | Condición |
|---:|---:|---:|---|
| 1 | 2.0 | 3.0 | Sistema estable |
| 2 | 2.5 | 3.0 | Mayor utilización |
| 3 | 2.9 | 3.0 | Cerca de saturación |

## Integrantes

## Autores: 
### [Iveth Zaragocin](https://github.com/ivecanahi)
### [Steeven Pardo](https://github.com/Dan1el17)
### [Anthony Yaguana](https://github.com/Anthony-YP)
### [Pedro Jiménez](https://github.com/Pedro27-J)
