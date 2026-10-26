package view;

import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Font;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import java.util.Locale;

import javax.imageio.ImageIO;

import model.ModeloExponencial;
import model.ResultadoHora;

/**
 * VISTA - Gráficas PNG dibujadas con Java2D (sin librerías externas).
 */
public class VistaGrafica {

    private static final int ANCHO = 1000, ALTO = 500, MARGEN = 60;
    private static final Color[] COLORES = {
            new Color(0x1f77b4), new Color(0xff7f0e), new Color(0x2ca02c),
            new Color(0xd62728), new Color(0x9467bd)};

    /** Índice I por hora, con las franjas de la tabla de reglas. */
    public void graficaIndice(String titulo, List<List<ResultadoHora>> series,
                              List<String> nombres, Path ruta) throws IOException {
        BufferedImage img = new BufferedImage(ANCHO, ALTO, BufferedImage.TYPE_INT_RGB);
        Graphics2D g = preparar(img, titulo);

        // PASO 1 - Franjas: Sin lluvia, Baja, Probable, Lluvia
        double[][] franjas = {{0, 0.40}, {0.40, 0.60}, {0.60, 0.75}, {0.75, 1.0}};
        Color[] colFranja = {new Color(0xd9ecd0), new Color(0xfbefc4),
                new Color(0xfbd9b5), new Color(0xf6c1c1)};
        for (int k = 0; k < franjas.length; k++) {
            int y1 = y(franjas[k][1], 0, 1), y0 = y(franjas[k][0], 0, 1);
            g.setColor(colFranja[k]);
            g.fillRect(MARGEN, y1, ANCHO - 2 * MARGEN, y0 - y1);
        }
        ejes(g, 0, 1);

        // PASO 2 - Una línea por cada modelo
        int nPuntos = series.get(0).size();
        for (int s = 0; s < series.size(); s++) {
            List<ResultadoHora> res = series.get(s);
            g.setColor(COLORES[s]);
            for (int i = 0; i < nPuntos; i++) {
                int px = x(i, nPuntos - 1), py = y(res.get(i).indice(), 0, 1);
                g.fillOval(px - 4, py - 4, 8, 8);
                if (i > 0) {
                    g.drawLine(x(i - 1, nPuntos - 1), y(res.get(i - 1).indice(), 0, 1), px, py);
                }
                if (series.size() == 1) {
                    g.drawString(String.format(Locale.US, "%.3f", res.get(i).indice()), px - 12, py - 8);
                }
            }
            g.drawString(nombres.get(s), MARGEN + 10, MARGEN + 20 + 18 * s);
        }

        // PASO 3 - Etiquetas del eje X (horas)
        g.setColor(Color.BLACK);
        for (int i = 0; i < nPuntos; i++) {
            g.drawString(series.get(0).get(i).hora(), x(i, nPuntos - 1) - 18, ALTO - MARGEN + 20);
        }
        guardar(g, img, ruta);
    }

    /** Curvas de crecimiento y decrecimiento para cada r. */
    public void graficaExponencial(Path ruta) throws IOException {
        BufferedImage img = new BufferedImage(ANCHO, ALTO, BufferedImage.TYPE_INT_RGB);
        Graphics2D g = preparar(img, "Modelo exponencial P(t) = P0·e^(rt)");
        double maxP = ModeloExponencial.poblacion(ModeloExponencial.T_MAX, ModeloExponencial.P0, 0.10);
        ejes(g, 0, maxP);

        int pasos = 240;
        double[] tasas = ModeloExponencial.TASAS_R;
        for (int s = 0; s < tasas.length; s++) {
            g.setColor(COLORES[s]);
            int prevX = 0, prevY = 0;
            for (int i = 0; i <= pasos; i++) {
                double t = ModeloExponencial.T_MAX * i / pasos;
                double p = ModeloExponencial.poblacion(t, ModeloExponencial.P0, tasas[s]);
                int px = x(i, pasos), py = y(p, 0, maxP);
                if (i > 0) g.drawLine(prevX, prevY, px, py);
                prevX = px;
                prevY = py;
            }
            g.drawString("r = " + tasas[s], MARGEN + 10, MARGEN + 20 + 18 * s);
        }
        g.setColor(Color.BLACK);
        for (int h = 0; h <= 24; h += 4) {
            g.drawString(h + " h", x(h, 24) - 10, ALTO - MARGEN + 20);
        }
        guardar(g, img, ruta);
    }

    // ---------------- utilidades de dibujo ----------------

    private Graphics2D preparar(BufferedImage img, String titulo) {
        Graphics2D g = img.createGraphics();
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        g.setColor(Color.WHITE);
        g.fillRect(0, 0, ANCHO, ALTO);
        g.setColor(Color.BLACK);
        g.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 16));
        g.drawString(titulo, MARGEN, 35);
        g.setFont(new Font(Font.SANS_SERIF, Font.PLAIN, 12));
        g.setStroke(new BasicStroke(2f));
        return g;
    }

    private void ejes(Graphics2D g, double yMin, double yMax) {
        g.setColor(Color.BLACK);
        g.drawLine(MARGEN, ALTO - MARGEN, ANCHO - MARGEN, ALTO - MARGEN);
        g.drawLine(MARGEN, MARGEN, MARGEN, ALTO - MARGEN);
        for (int k = 0; k <= 4; k++) {
            double v = yMin + (yMax - yMin) * k / 4;
            g.drawString(String.format(Locale.US, "%.2f", v), 5, y(v, yMin, yMax) + 4);
        }
    }

    private int x(double i, double iMax) {
        return (int) (MARGEN + i / iMax * (ANCHO - 2 * MARGEN));
    }

    private int y(double v, double yMin, double yMax) {
        return (int) (ALTO - MARGEN - (v - yMin) / (yMax - yMin) * (ALTO - 2 * MARGEN));
    }

    private void guardar(Graphics2D g, BufferedImage img, Path ruta) throws IOException {
        g.dispose();
        ImageIO.write(img, "png", ruta.toFile());
    }
}
