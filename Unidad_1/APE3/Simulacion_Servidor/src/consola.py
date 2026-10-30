"""Presentación de los resultados en la consola con la biblioteca rich.

Cada función recibe opcionalmente una consola; las pruebas pasan una consola
que graba el texto para poder revisarlo.
"""

from rich import box
from rich.columns import Columns
from rich.console import Console, Group
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

# Consola compartida por todo el programa
CONSOLA = Console()


def color_error(error):
    """Color según el error %: verde (< 10 %), amarillo (< 20 %) o rojo."""
    if error < 10:
        return "green"
    if error < 20:
        return "yellow"
    return "red"


def color_utilizacion(rho):
    """Color según la utilización: verde (< 0.8), amarillo (< 0.95) o rojo."""
    if rho < 0.8:
        return "green"
    if rho < 0.95:
        return "yellow"
    return "red"


def barra_utilizacion(rho, ancho=30):
    """Barra de texto que muestra qué tan ocupado está el servidor (rho)."""
    # Cantidad de bloques llenos proporcional a rho; el color avisa la saturación
    llenos = round(rho * ancho)
    color = color_utilizacion(rho)
    barra = Text("█" * llenos, style=color)
    barra.append("░" * (ancho - llenos), style="dim")
    barra.append(f" {rho:.1%}", style=f"bold {color}")
    return barra


def mostrar_menu(escenarios, tiempo_sim, semilla, consola=CONSOLA):
    """Panel con los escenarios, una opción para todos, 0 para salir y los parámetros."""
    tabla = Table(box=box.SIMPLE_HEAVY, header_style="bold cyan", show_edge=False)
    tabla.add_column("Opción", justify="right", style="bold cyan")
    tabla.add_column("Escenario")
    tabla.add_column("λ", justify="right")
    tabla.add_column("μ", justify="right")
    tabla.add_column("ρ", justify="right")
    for esc in escenarios:
        rho = esc["lam"] / esc["mu"]
        tabla.add_row(
            str(esc["escenario"]),
            f"Escenario {esc['escenario']} · {esc['condicion']}",
            f"{esc['lam']:.1f}",
            f"{esc['mu']:.1f}",
            Text(f"{rho:.3f}", style=color_utilizacion(rho)),
        )
    tabla.add_row(str(len(escenarios) + 1), "Todos los escenarios y comparación", "", "", "")
    tabla.add_row("0", "Salir", "", "", "")

    parametros = Text.assemble(
        ("Tiempo de simulación: ", "dim"),
        (str(tiempo_sim), "bold"),
        ("   ·   Semilla: ", "dim"),
        (str(semilla), "bold"),
    )
    consola.print()
    consola.print(
        Panel(
            Group(tabla, Text(), parametros),
            title="[bold]Simulación de una cola M/M/1 con SimPy[/bold]",
            subtitle="APE 3 · Simulación",
            border_style="cyan",
            padding=(1, 2),
            expand=False,
        )
    )


class PromptMenu(Prompt):
    """Prompt de rich con el aviso de opción inválida en español."""

    illegal_choice_message = "[prompt.invalid.choice]Opción no válida, elige una de la lista"


def pedir_opcion(escenarios, consola=CONSOLA, stream=None):
    """Pide una opción del menú; vuelve a preguntar si no es válida."""
    # Opciones válidas: 0 (salir), 1..n (un escenario) y n+1 (todos)
    opciones = [str(i) for i in range(len(escenarios) + 2)]
    return int(PromptMenu.ask("Elige una opción", choices=opciones, console=consola, stream=stream))


def esperar_enter(consola=CONSOLA, stream=None):
    """Pausa hasta que el usuario presiona Enter, para leer los resultados."""
    consola.print()
    consola.input("[dim]Presiona Enter para volver al menú[/dim] ", stream=stream)


def mostrar_escenario(esc, resultado, consola=CONSOLA):
    """Panel de un escenario: utilización, clientes atendidos y Wq/Lq teórico vs. simulado."""
    tabla = Table(box=box.ROUNDED, header_style="bold")
    tabla.add_column("Métrica")
    tabla.add_column("Teórico", justify="right", style="cyan")
    tabla.add_column("Simulado", justify="right", style="magenta")
    tabla.add_column("Error", justify="right")
    # (nombre visible, clave teórica, clave simulada, clave del error)
    filas = [
        ("Wq · espera en cola", "Wq", "espera_promedio", "error_Wq_%"),
        ("Lq · clientes en cola", "Lq", "cola_promedio", "error_Lq_%"),
    ]
    for nombre, teorico, simulado, error in filas:
        e = resultado[error]
        tabla.add_row(
            nombre,
            f"{resultado[teorico]:.3f}",
            f"{resultado[simulado]:.3f}",
            Text(f"{e:.1f}%", style=color_error(e)),
        )

    resumen = Text.assemble(
        ("Utilización ρ  ", "bold"), barra_utilizacion(resultado["rho"]), "\n",
        ("Clientes atendidos  ", "bold"), (f"{resultado['clientes_atendidos']:,}", ""),
    )
    consola.print()
    consola.print(
        Panel(
            Group(resumen, Text(), tabla),
            title=f"[bold]Escenario {esc['escenario']}[/bold] · {esc['condicion']}",
            subtitle=f"λ = {esc['lam']:.1f}   μ = {esc['mu']:.1f}",
            border_style="blue",
            padding=(1, 2),
            expand=False,
        )
    )


def mostrar_resumen_escenarios(pares, consola=CONSOLA):
    """Paneles compactos lado a lado, uno por cada par (escenario, resultado)."""
    paneles = []
    for esc, r in pares:
        # Cada línea: teórico / simulado / error, con el error coloreado
        lineas = [
            Text.assemble(("ρ  ", "bold"), barra_utilizacion(r["rho"], ancho=12)),
            Text.assemble(("Clientes  ", "bold"), f"{r['clientes_atendidos']:,}"),
        ]
        for nombre, teorico, simulado, error in [
            ("Wq", "Wq", "espera_promedio", "error_Wq_%"),
            ("Lq", "Lq", "cola_promedio", "error_Lq_%"),
        ]:
            e = r[error]
            lineas.append(
                Text.assemble(
                    (f"{nombre}  ", "bold"),
                    (f"{r[teorico]:.3f}", "cyan"),
                    " / ",
                    (f"{r[simulado]:.3f}", "magenta"),
                    " / ",
                    (f"{e:.1f}%", color_error(e)),
                )
            )
        paneles.append(
            Panel(
                Text("\n").join(lineas),
                title=f"[bold]Escenario {esc['escenario']}[/bold]",
                subtitle=esc["condicion"],
                border_style="blue",
                padding=(0, 1),
                expand=False,
            )
        )
    consola.print()
    consola.print(Columns(paneles))
    consola.print("[dim]Wq y Lq: teórico / simulado / error[/dim]")


def mostrar_inestable(numero, lam, mu, consola=CONSOLA):
    """Aviso en rojo para un escenario que no se simula porque lam >= mu."""
    consola.print(
        Panel(
            f"λ = {lam} ≥ μ = {mu}: el sistema no es estable y la cola crecería sin límite.",
            title=f"[bold]Escenario {numero}[/bold] · omitido",
            border_style="red",
            expand=False,
        )
    )


def mostrar_tabla(resultados, consola=CONSOLA):
    """Tabla final que compara las métricas teóricas y simuladas de todos los escenarios."""
    tabla = Table(
        title="[bold]Comparación teórico vs. simulado[/bold]",
        box=box.ROUNDED,
        header_style="bold",
        show_lines=False,
    )
    tabla.add_column("Esc.", justify="center")
    tabla.add_column("λ", justify="right")
    tabla.add_column("ρ", justify="right")
    for columna in ["L", "Lq", "W", "Wq"]:
        tabla.add_column(columna, justify="right", style="cyan")
    tabla.add_column("Wq sim.", justify="right", style="magenta")
    tabla.add_column("Lq sim.", justify="right", style="magenta")
    tabla.add_column("Error Wq", justify="right")
    tabla.add_column("Error Lq", justify="right")

    for r in resultados:
        tabla.add_row(
            str(r["escenario"]),
            f"{r['lam']:.1f}",
            f"{r['rho']:.3f}",
            f"{r['L']:.3f}",
            f"{r['Lq']:.3f}",
            f"{r['W']:.3f}",
            f"{r['Wq']:.3f}",
            f"{r['espera_promedio']:.3f}",
            f"{r['cola_promedio']:.3f}",
            Text(f"{r['error_Wq_%']:.1f}%", style=color_error(r["error_Wq_%"])),
            Text(f"{r['error_Lq_%']:.1f}%", style=color_error(r["error_Lq_%"])),
        )

    consola.print()
    consola.print(tabla)
    consola.print(
        "[cyan]■[/cyan] teórico   [magenta]■[/magenta] simulado   "
        "error: [green]< 10 %[/green]  [yellow]< 20 %[/yellow]  [red]≥ 20 %[/red]"
    )


def mostrar_archivos(rutas, consola=CONSOLA):
    """Lista de las gráficas y tablas que se guardaron en disco."""
    lista = Text("\n").join(Text.assemble(("✔ ", "green"), ruta) for ruta in rutas)
    consola.print()
    consola.print(
        Panel(
            lista,
            title="[bold]Archivos generados[/bold]",
            border_style="green",
            padding=(1, 2),
            expand=False,
        )
    )
