"""Parte 3: exportación de resultados a CSV, gráfica S(t), I(t), R(t) y reporte HTML."""

import csv
from pathlib import Path
from string import Template

import matplotlib

matplotlib.use("Agg")  # Backend sin ventana, solo para guardar archivos
import matplotlib.pyplot as plt  # noqa: E402

from model import SIRParameters, StepResult  # noqa: E402

HEADER = ["tiempo", "susceptibles", "infectados", "recuperados"]

# Paleta compartida por la gráfica y el reporte
COLOR_S = "#16a34a"
COLOR_I = "#e11d48"
COLOR_R = "#6366f1"


class CsvExporter:
    """Escribe los resultados de la simulación en un archivo CSV."""

    @staticmethod
    def export(results: list[StepResult], path) -> None:
        """Guarda una fila por instante con el encabezado de la guía."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(HEADER)
            for step in results:
                writer.writerow(
                    [step.time, step.susceptible, step.infected, step.recovered]
                )


class ChartView:
    """Genera la gráfica de S(t), I(t) y R(t)."""

    @staticmethod
    def plot(results: list[StepResult], path) -> None:
        """Dibuja las tres curvas, marca el pico de infectados y guarda la imagen."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        times = [step.time for step in results]
        infected = [s.infected for s in results]
        peak = max(results, key=lambda step: step.infected)

        fig, ax = plt.subplots(figsize=(10, 5.2))
        ax.plot(times, [s.susceptible for s in results], label="Susceptibles",
                color=COLOR_S, linewidth=2.4)
        ax.plot(times, infected, label="Infectados", color=COLOR_I, linewidth=2.4)
        ax.fill_between(times, infected, color=COLOR_I, alpha=0.12)
        ax.plot(times, [s.recovered for s in results], label="Recuperados",
                color=COLOR_R, linewidth=2.4)
        ax.scatter([peak.time], [peak.infected], color=COLOR_I, s=50, zorder=5)
        ax.annotate(
            f"Pico: {peak.infected} infectados (t = {peak.time})",
            xy=(peak.time, peak.infected),
            xytext=(peak.time + 8, peak.infected + 14),
            arrowprops={"arrowstyle": "->", "color": "#475569"},
            fontsize=10, color="#334155",
        )
        ax.set_title("Modelo SIR (Python + SimPy)", fontsize=14, fontweight="bold",
                     loc="left", color="#0f172a")
        ax.set_xlabel("Tiempo", color="#475569")
        ax.set_ylabel("Individuos", color="#475569")
        ax.set_xlim(times[0], times[-1])
        ax.set_ylim(0, max(max(s.susceptible, s.infected, s.recovered) for s in results) + 5)
        ax.grid(True, color="#e2e8f0", linewidth=0.8)
        ax.tick_params(colors="#475569")
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color("#cbd5e1")
        ax.legend(frameon=False, loc="center right")
        fig.tight_layout()
        fig.savefig(path, dpi=150)
        plt.close(fig)


REPORT_TEMPLATE = Template("""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Modelo SIR en Python</title>
<style>
  :root {
    --bg: #f4f6fb; --card: #ffffff; --ink: #0f172a; --muted: #64748b; --line: #e2e8f0;
    --soft: #f1f5f9; --s: #16a34a; --i: #e11d48; --r: #6366f1;
    --hero-1: #0f172a; --hero-2: #312e81;
    --shadow: 0 1px 2px rgba(15, 23, 42, .06), 0 8px 24px rgba(15, 23, 42, .06);
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #0b1120; --card: #111827; --ink: #e5e7eb; --muted: #94a3b8; --line: #1f2937;
      --soft: #1e293b; --s: #22c55e; --i: #fb7185; --r: #818cf8;
      --hero-1: #020617; --hero-2: #1e1b4b; --shadow: none;
    }
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--bg); color: var(--ink); line-height: 1.6;
         font-family: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif; }
  .wrap { max-width: 1040px; margin: 0 auto; padding: 0 16px 48px; }

  .hero { background: radial-gradient(circle at 85% 20%, rgba(225, 29, 72, .35), transparent 40%),
                      linear-gradient(135deg, var(--hero-1), var(--hero-2));
          color: #fff; padding: 48px 0 88px; }
  .hero .wrap { display: flex; gap: 24px; align-items: center; justify-content: space-between;
                flex-wrap: wrap; padding-bottom: 0; }
  .eyebrow { text-transform: uppercase; letter-spacing: .12em; font-size: .75rem; opacity: .75; }
  .hero h1 { font-size: clamp(2rem, 5vw, 3rem); line-height: 1.1; margin: 8px 0 12px; }
  .hero p { max-width: 560px; opacity: .85; margin: 0 0 16px; }
  .chips { display: flex; gap: 8px; flex-wrap: wrap; }
  .chip { background: rgba(255, 255, 255, .12); border: 1px solid rgba(255, 255, 255, .2);
          border-radius: 999px; padding: 4px 12px; font-size: .8rem; }
  .r0 { text-align: center; background: rgba(255, 255, 255, .08); border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, .2); padding: 20px 28px; }
  .r0 b { display: block; font-size: 3.2rem; line-height: 1; }
  .r0 span { font-size: .85rem; opacity: .8; }

  .card { background: var(--card); border: 1px solid var(--line); border-radius: 16px;
          box-shadow: var(--shadow); padding: 24px; margin-top: 20px; }
  .lift { margin-top: -56px; }
  h2 { font-size: 1.25rem; margin: 0 0 4px; }
  .lead { color: var(--muted); margin: 0 0 20px; }
  .grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }

  .flow { display: flex; align-items: center; justify-content: center; gap: 8px; flex-wrap: wrap;
          padding: 8px 0 4px; }
  .state { margin: 0; width: 180px; text-align: center; }
  .face { display: block; width: 112px; height: 112px; margin: 0 auto 10px;
          filter: drop-shadow(0 8px 14px rgba(15, 23, 42, .18)); }
  .state figcaption { color: var(--muted); font-size: .85rem; line-height: 1.4; }
  .state figcaption b { display: block; color: var(--ink); font-size: 1rem; margin-bottom: 2px; }
  .arrow { text-align: center; color: var(--muted); font-size: .8rem; min-width: 110px; }
  .arrow i { display: block; font-style: normal; font-size: 1.6rem; color: var(--ink); line-height: 1; }
  .mini { display: block; width: 30px; height: 30px; margin: 0 auto 4px; }

  .cycle { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
  .panel { background: var(--soft); border-radius: 14px; padding: 18px; }
  .panel h3 { margin: 0 0 14px; font-size: 1.05rem; }
  .scene { display: flex; align-items: center; justify-content: center; gap: 10px; min-height: 72px; }
  .face-sm { width: 64px; height: 64px; flex: none; }
  .link { flex: 1; max-width: 170px; border-top: 3px dashed var(--muted); text-align: center; }
  .link span { display: block; margin-top: 4px; font-size: .75rem; color: var(--muted); line-height: 1.3; }
  .decision { display: flex; gap: 14px; align-items: center; margin: 14px 0; padding: 10px 14px;
              background: var(--card); border: 1px solid var(--line); border-radius: 12px; font-size: .9rem; }
  .dice { width: 42px; height: 42px; flex: none; color: var(--ink); transform: rotate(-12deg); }
  .outcomes { display: grid; gap: 10px; grid-template-columns: 1fr 1fr; }
  .outcomes > div { display: flex; gap: 8px; align-items: center; padding: 8px 10px; font-size: .85rem;
                    line-height: 1.3; background: var(--card); border: 1px solid var(--line); border-radius: 12px; }
  .outcomes b { display: block; }
  .face-xs { width: 36px; height: 36px; flex: none; }

  .pops { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); margin-top: 8px; }
  .pop { margin: 0; padding: 16px; text-align: center; background: var(--soft); border-radius: 14px; }
  .pop svg { width: 100%; max-width: 220px; height: auto; }
  .pop figcaption { color: var(--muted); font-size: .85rem; }
  .pop figcaption b { display: block; color: var(--ink); font-size: .95rem; }
  use.ps { color: var(--s); } use.pi { color: var(--i); } use.pr { color: var(--r); }
  h3.sub { font-size: 1.05rem; margin: 28px 0 4px; }

  .eq { background: var(--soft); border-radius: 12px; padding: 14px 16px; }
  .eq code { font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 1rem; }
  .eq small { display: block; color: var(--muted); margin-top: 4px; }

  .params { display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); }
  .param { border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; }
  .param span { color: var(--muted); font-size: .8rem; }
  .param b { display: block; font-size: 1.4rem; }

  .steps { list-style: none; margin: 0; padding: 0; counter-reset: step; }
  .steps li { position: relative; padding: 0 0 18px 48px; counter-increment: step; }
  .steps li::before { content: counter(step); position: absolute; left: 0; top: 0; width: 32px;
                      height: 32px; border-radius: 50%; display: grid; place-content: center;
                      background: var(--r); color: #fff; font-weight: 700; font-size: .85rem; }
  .steps li:not(:last-child)::after { content: ""; position: absolute; left: 15px; top: 34px;
                                      bottom: 2px; width: 2px; background: var(--line); }
  .steps b { display: block; }
  .steps span { color: var(--muted); }
  .note { background: var(--soft); border-left: 4px solid var(--r); border-radius: 8px;
          padding: 12px 16px; margin-top: 8px; }

  .kpis { display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); }
  .kpi { border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px;
         border-top: 4px solid var(--accent, var(--hero-2)); }
  .kpi span { color: var(--muted); font-size: .8rem; }
  .kpi b { display: block; font-size: 2rem; line-height: 1.2; color: var(--accent, var(--ink)); }
  .kpi small { color: var(--muted); }
  .chart { margin-top: 20px; background: #fff; border-radius: 12px; padding: 8px; }
  .chart img { display: block; width: 100%; height: auto; }

  .table-wrap { max-height: 420px; overflow: auto; border: 1px solid var(--line); border-radius: 12px; }
  table { border-collapse: collapse; width: 100%; font-variant-numeric: tabular-nums; }
  th { position: sticky; top: 0; background: var(--soft); text-align: right; font-size: .8rem;
       text-transform: uppercase; letter-spacing: .05em; color: var(--muted); }
  th, td { padding: 6px 14px; text-align: right; border-bottom: 1px solid var(--line); }
  th:last-child, td:last-child { text-align: left; width: 38%; }
  tbody tr:hover { background: var(--soft); }
  .bar { display: flex; height: 10px; border-radius: 999px; overflow: hidden; background: var(--line); }
  .bar .s { background: var(--s); } .bar .i { background: var(--i); } .bar .r { background: var(--r); }
  .legend { display: flex; gap: 16px; flex-wrap: wrap; color: var(--muted); font-size: .85rem;
            margin-bottom: 12px; }
  .dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; }

  footer { text-align: center; color: var(--muted); font-size: .85rem; margin-top: 32px; }
  code.file { background: var(--soft); padding: 1px 6px; border-radius: 6px; }
</style>
</head>
<body>
<svg width="0" height="0" style="position: absolute" aria-hidden="true">
  <defs>
    <symbol id="person" viewBox="0 0 20 26">
      <circle cx="10" cy="6" r="5" fill="currentColor"/>
      <path d="M1 26 Q1 13 10 13 Q19 13 19 26 Z" fill="currentColor"/>
    </symbol>
    <symbol id="face-s" viewBox="0 0 100 100">
      <circle cx="50" cy="50" r="46" style="fill: var(--s)"/>
      <circle cx="35" cy="42" r="6" fill="#fff"/><circle cx="65" cy="42" r="6" fill="#fff"/>
      <path d="M30 60 Q50 80 70 60" stroke="#fff" stroke-width="6" fill="none" stroke-linecap="round"/>
    </symbol>
    <symbol id="face-i" viewBox="0 0 100 100">
      <circle cx="50" cy="50" r="46" style="fill: var(--i)"/>
      <path d="M27 42 L41 42 M59 42 L73 42" stroke="#fff" stroke-width="6" stroke-linecap="round"/>
      <path d="M32 70 Q41 62 50 70 Q59 78 68 70" stroke="#fff" stroke-width="6" fill="none" stroke-linecap="round"/>
      <circle cx="25" cy="56" r="7" fill="#fff" opacity=".3"/><circle cx="75" cy="56" r="7" fill="#fff" opacity=".3"/>
      <g transform="translate(-6 8) rotate(30 82 22)">
        <rect x="77" y="2" width="10" height="32" rx="5" fill="#fff" stroke="#0f172a" stroke-width="2"/>
        <circle cx="82" cy="35" r="7" fill="#fff" stroke="#0f172a" stroke-width="2"/>
        <rect x="80" y="12" width="4" height="22" fill="#e11d48"/><circle cx="82" cy="35" r="4" fill="#e11d48"/>
      </g>
    </symbol>
    <symbol id="face-r" viewBox="0 0 100 100">
      <circle cx="50" cy="50" r="46" style="fill: var(--r)"/>
      <path d="M28 44 Q35 36 42 44 M58 44 Q65 36 72 44" stroke="#fff" stroke-width="6" fill="none" stroke-linecap="round"/>
      <path d="M32 60 Q50 76 68 60" stroke="#fff" stroke-width="6" fill="none" stroke-linecap="round"/>
      <path d="M80 58 L97 64 L97 77 Q97 91 80 99 Q63 91 63 77 L63 64 Z" fill="#fff" stroke="#0f172a" stroke-width="2"/>
      <path d="M72 78 L78 84 L89 71" stroke="#16a34a" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    </symbol>
    <symbol id="dice" viewBox="0 0 40 40">
      <rect x="2" y="2" width="36" height="36" rx="8" fill="#fff" stroke="currentColor" stroke-width="3"/>
      <circle cx="12" cy="12" r="3.2" fill="#0f172a"/><circle cx="28" cy="12" r="3.2" fill="#0f172a"/>
      <circle cx="20" cy="20" r="3.2" fill="#0f172a"/>
      <circle cx="12" cy="28" r="3.2" fill="#0f172a"/><circle cx="28" cy="28" r="3.2" fill="#0f172a"/>
    </symbol>
    <symbol id="virus" viewBox="0 0 40 40">
      <g stroke="currentColor" stroke-width="3" stroke-linecap="round">
        <path d="M20 20 L36 20 M20 20 L31.3 31.3 M20 20 L20 36 M20 20 L8.7 31.3 M20 20 L4 20 M20 20 L8.7 8.7 M20 20 L20 4 M20 20 L31.3 8.7"/>
      </g>
      <circle cx="20" cy="20" r="10" fill="currentColor"/>
      <circle cx="16" cy="17" r="2.5" fill="#fff" opacity=".6"/><circle cx="23" cy="23" r="2" fill="#fff" opacity=".6"/>
    </symbol>
    <symbol id="heart" viewBox="0 0 40 40">
      <path d="M20 34 C4 24 4 10 13 8 C17 7 20 10 20 13 C20 10 23 7 27 8 C36 10 36 24 20 34 Z" fill="currentColor"/>
    </symbol>
  </defs>
</svg>
<header class="hero">
  <div class="wrap">
    <div>
      <div class="eyebrow">Práctica 04 · Simulación · Unidad 1</div>
      <h1>Modelo epidemiológico SIR</h1>
      <p>Simulación discreta de la propagación de una infección en una población de
      $population personas, implementada en Python con SimPy.</p>
      <div class="chips">
        <span class="chip">Python</span><span class="chip">SimPy</span>
        <span class="chip">Matplotlib</span><span class="chip">CSV → NetLogo</span>
      </div>
    </div>
    <div class="r0"><span>Número reproductivo básico</span><b>$r0_short</b><span>R₀ = β / γ = $r0</span></div>
  </div>
</header>

<main class="wrap">
  <section class="card lift">
    <h2>¿Qué hace la práctica?</h2>
    <p class="lead">Cada individuo está siempre en uno de tres estados y solo puede avanzar en un sentido.
    La población total se mantiene: N = S + I + R.</p>
    <div class="flow">
      <figure class="state">
        <svg class="face"><use href="#face-s"/></svg>
        <figcaption><b>S · Susceptible</b>Está sano, pero se puede contagiar.</figcaption>
      </figure>
      <div class="arrow"><svg class="mini" style="color: var(--i)"><use href="#virus"/></svg><i>→</i>contagio<br>β = $beta</div>
      <figure class="state">
        <svg class="face"><use href="#face-i"/></svg>
        <figcaption><b>I · Infectado</b>Está enfermo y puede contagiar a otros.</figcaption>
      </figure>
      <div class="arrow"><svg class="mini" style="color: var(--r)"><use href="#heart"/></svg><i>→</i>recuperación<br>γ = $gamma</div>
      <figure class="state">
        <svg class="face"><use href="#face-r"/></svg>
        <figcaption><b>R · Recuperado</b>Ya se curó y no vuelve a contagiarse.</figcaption>
      </figure>
    </div>
  </section>

  <section class="card">
    <h2>Modelo matemático</h2>
    <p class="lead">Las ecuaciones describen el modelo continuo; en el código se aproxima con pasos de tiempo discretos.</p>
    <div class="grid">
      <div class="eq"><code>dS/dt = −β·S·I/N</code><small>Los susceptibles disminuyen con cada contagio.</small></div>
      <div class="eq"><code>dI/dt = β·S·I/N − γ·I</code><small>Entran nuevos contagios y salen los recuperados.</small></div>
      <div class="eq"><code>dR/dt = γ·I</code><small>Los recuperados crecen a ritmo γ.</small></div>
    </div>
  </section>

  <section class="card">
    <h2>Parámetros</h2>
    <p class="lead">Los mismos valores se usan en Python y NetLogo para poder comparar.</p>
    <div class="params">
      <div class="param"><span>Población (N)</span><b>$population</b></div>
      <div class="param"><span>Infectados iniciales</span><b>$initial_infected</b></div>
      <div class="param"><span>β · tasa de infección</span><b>$beta</b></div>
      <div class="param"><span>γ · tasa de recuperación</span><b>$gamma</b></div>
      <div class="param"><span>Tiempo de simulación</span><b>0 – $max_time</b></div>
      <div class="param"><span>Semilla aleatoria</span><b>$seed</b></div>
    </div>
  </section>

  <section class="card">
    <h2>¿Cómo funciona cada paso?</h2>
    <p class="lead">El proceso de SimPy repite este ciclo desde t = 0 hasta t = $max_time.</p>
    <ol class="steps">
      <li><b>📋 Registrar</b><span>Se guardan el tiempo y los conteos de S, I y R.</span></li>
      <li><b>📸 Copiar el estado</b><span>Se toma una foto de la población antes de cambiar nada.</span></li>
      <li><b>🦠 Contagiar</b><span>Cada infectado elige un contacto al azar; si es susceptible y
          un número aleatorio es menor que β, se contagia.</span></li>
      <li><b>💜 Recuperar</b><span>Cada infectado se recupera si un número aleatorio es menor que γ.</span></li>
      <li><b>⏱️ Avanzar el reloj</b><span><code>env.timeout(1)</code> pasa al siguiente instante.</span></li>
    </ol>
    <div class="note">La copia del estado evita que alguien contagiado en este paso contagie a otro
    en ese mismo paso: todos los cambios se calculan sobre la foto inicial.</div>
  </section>

  <section class="card">
    <h2>Lo que le pasa a un infectado en cada paso</h2>
    <p class="lead">El azar decide todo: se "tira un dado" que da un número entre 0 y 1 y se compara con β o γ.</p>
    <div class="cycle">
      <div class="panel">
        <h3>1 · Intenta contagiar</h3>
        <div class="scene">
          <svg class="face-sm"><use href="#face-i"/></svg>
          <div class="link"><span>elige a alguien<br>al azar</span></div>
          <svg class="face-sm"><use href="#face-s"/></svg>
        </div>
        <div class="decision">
          <svg class="dice"><use href="#dice"/></svg>
          <div>Si el contacto está sano, se tira el dado:<br><b>¿salió menos que β = $beta?</b></div>
        </div>
        <div class="outcomes">
          <div><svg class="face-xs"><use href="#face-i"/></svg><span><b>Sí · $beta_pct%</b>se contagia</span></div>
          <div><svg class="face-xs"><use href="#face-s"/></svg><span><b>No · $beta_no_pct%</b>sigue sano</span></div>
        </div>
      </div>
      <div class="panel">
        <h3>2 · Intenta recuperarse</h3>
        <div class="scene">
          <svg class="face-sm"><use href="#face-i"/></svg>
        </div>
        <div class="decision">
          <svg class="dice"><use href="#dice"/></svg>
          <div>Se tira el dado otra vez:<br><b>¿salió menos que γ = $gamma?</b></div>
        </div>
        <div class="outcomes">
          <div><svg class="face-xs"><use href="#face-r"/></svg><span><b>Sí · $gamma_pct%</b>se recupera</span></div>
          <div><svg class="face-xs"><use href="#face-i"/></svg><span><b>No · $gamma_no_pct%</b>sigue enfermo</span></div>
        </div>
      </div>
    </div>
    <div class="note">Como en promedio un infectado tarda 1/γ = $duration pasos en recuperarse y en cada paso
    contagia con probabilidad β, contagia a unas β/γ = $r0_short personas: ese es el R₀.</div>
  </section>

  <section class="card">
    <h2>Resultados</h2>
    <p class="lead">Con semilla $seed la simulación siempre produce exactamente estos valores.</p>
    <div class="kpis">
      <div class="kpi" style="--accent: var(--i)"><span>Pico de infectados</span><b>$peak_infected</b><small>en t = $peak_time</small></div>
      <div class="kpi"><span>Fin del brote</span><b>$end_time</b><small>primer instante sin infectados</small></div>
      <div class="kpi"><span>Tasa de ataque</span><b>$attack_rate%</b><small>se infectaron alguna vez</small></div>
      <div class="kpi" style="--accent: var(--s)"><span>Susceptibles finales</span><b>$final_s</b><small>nunca se infectaron</small></div>
      <div class="kpi" style="--accent: var(--r)"><span>Recuperados finales</span><b>$final_r</b><small>con $final_i infectados al final</small></div>
    </div>
    <div class="chart"><img src="$chart_file" alt="Gráfica de S(t), I(t) y R(t)"></div>

    <h3 class="sub">La población, persona por persona</h3>
    <p class="lead">Cada muñequito es una de las $population personas de la simulación.</p>
    <div class="pops">
      <figure class="pop">$grid_start<figcaption><b>Al inicio · t = $start_time</b>$caption_start</figcaption></figure>
      <figure class="pop">$grid_peak<figcaption><b>En el pico · t = $peak_time</b>$caption_peak</figcaption></figure>
      <figure class="pop">$grid_end<figcaption><b>Al final · t = $end_time_value</b>$caption_end</figcaption></figure>
    </div>
  </section>

  <section class="card">
    <h2>Datos de la simulación</h2>
    <p class="lead">$rows filas, las mismas que se exportan en <code class="file">resultados_python.csv</code>.</p>
    <div class="legend">
      <span><i class="dot" style="background: var(--s)"></i>Susceptibles</span>
      <span><i class="dot" style="background: var(--i)"></i>Infectados</span>
      <span><i class="dot" style="background: var(--r)"></i>Recuperados</span>
    </div>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Tiempo</th><th>S</th><th>I</th><th>R</th><th>Distribución</th></tr></thead>
        <tbody>
$table_rows
        </tbody>
      </table>
    </div>
  </section>

  <footer>Generado por <code class="file">main.py</code> · Python + SimPy · semilla $seed</footer>
</main>
</body>
</html>
""")


class ReportView:
    """Genera una página HTML que explica la práctica y muestra los resultados."""

    @staticmethod
    def summary(results: list[StepResult]) -> dict:
        """Pico de infectados, fin del brote, tasa de ataque y estado final."""
        peak = max(results, key=lambda step: step.infected)
        first, final = results[0], results[-1]
        population = first.susceptible + first.infected + first.recovered
        end_time = next((step.time for step in results if step.infected == 0), None)
        return {
            "peak_infected": peak.infected,
            "peak_time": peak.time,
            "end_time": end_time,
            "attack_rate": round(100 * (population - final.susceptible) / population, 1),
            "final": final,
        }

    @staticmethod
    def population_grid(step: StepResult, columns: int = 10) -> str:
        """SVG con un muñequito por persona, coloreado según su estado."""
        states = ["ps"] * step.susceptible + ["pi"] * step.infected + ["pr"] * step.recovered
        rows = -(-len(states) // columns)  # división redondeando hacia arriba
        people = "".join(
            f'<use href="#person" x="{2 + (n % columns) * 24}" y="{2 + (n // columns) * 30}" '
            f'width="20" height="26" class="{css}"/>'
            for n, css in enumerate(states)
        )
        return (
            f'<svg viewBox="0 0 {columns * 24} {rows * 30}" role="img" '
            f'aria-label="{step.susceptible} S, {step.infected} I, {step.recovered} R">{people}</svg>'
        )

    @staticmethod
    def _caption(step: StepResult) -> str:
        return (
            f'<span style="color: var(--s)">{step.susceptible} S</span> · '
            f'<span style="color: var(--i)">{step.infected} I</span> · '
            f'<span style="color: var(--r)">{step.recovered} R</span>'
        )

    @staticmethod
    def _row(step: StepResult, population: int) -> str:
        """Fila de la tabla con una barra apilada S/I/R."""
        bar = "".join(
            f'<span class="{css}" style="width: {100 * value / population:.1f}%"></span>'
            for css, value in (("s", step.susceptible), ("i", step.infected), ("r", step.recovered))
        )
        return (
            f'          <tr class="row"><td>{step.time}</td><td>{step.susceptible}</td>'
            f"<td>{step.infected}</td><td>{step.recovered}</td>"
            f'<td><div class="bar">{bar}</div></td></tr>'
        )

    @staticmethod
    def render(
        results: list[StepResult],
        params: SIRParameters,
        path,
        chart_file: str = "grafica_sir_python.png",
    ) -> None:
        """Escribe el reporte; `chart_file` es la ruta de la gráfica relativa al HTML."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        summary = ReportView.summary(results)
        final = summary["final"]
        r0 = params.beta / params.gamma
        end_time = summary["end_time"]
        start = results[0]
        peak = next(s for s in results if s.time == summary["peak_time"])
        html = REPORT_TEMPLATE.substitute(
            population=params.population,
            initial_infected=params.initial_infected,
            beta=f"{params.beta:.2f}",
            gamma=f"{params.gamma:.2f}",
            max_time=params.max_time,
            seed=params.seed,
            r0=f"{r0:.2f}",
            r0_short=f"{r0:g}",
            peak_infected=summary["peak_infected"],
            peak_time=summary["peak_time"],
            end_time=f"t = {end_time}" if end_time is not None else "—",
            attack_rate=f"{summary['attack_rate']:g}",
            final_s=final.susceptible,
            final_i=final.infected,
            final_r=final.recovered,
            chart_file=chart_file,
            beta_pct=f"{params.beta * 100:g}",
            beta_no_pct=f"{100 - params.beta * 100:g}",
            gamma_pct=f"{params.gamma * 100:g}",
            gamma_no_pct=f"{100 - params.gamma * 100:g}",
            duration=f"{1 / params.gamma:g}",
            start_time=start.time,
            end_time_value=final.time,
            grid_start=ReportView.population_grid(start),
            grid_peak=ReportView.population_grid(peak),
            grid_end=ReportView.population_grid(final),
            caption_start=ReportView._caption(start),
            caption_peak=ReportView._caption(peak),
            caption_end=ReportView._caption(final),
            rows=len(results),
            table_rows="\n".join(ReportView._row(s, params.population) for s in results),
        )
        path.write_text(html, encoding="utf-8")
