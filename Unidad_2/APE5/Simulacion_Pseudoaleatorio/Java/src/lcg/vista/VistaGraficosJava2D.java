package lcg.vista;

import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Font;
import java.awt.FontMetrics;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.geom.AffineTransform;
import java.awt.geom.Ellipse2D;
import java.awt.geom.Line2D;
import java.awt.geom.Rectangle2D;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Collections;
import java.util.List;

import javax.imageio.ImageIO;

import lcg.modelo.Observacion;
import lcg.modelo.ResumenEstadistico;
import lcg.util.FormatoDecimal;

/**
 * Implementación de {@link VistaGraficos} con Java2D (incluido en el JDK, sin librerías externas).
 *
 * <p>Dibuja en una imagen en memoria y la guarda como PNG, por lo que no necesita
 * pantalla. Usa la misma paleta que las gráficas de la versión Python.
 */
public final class VistaGraficosJava2D implements VistaGraficos {

    private static final Color SUPERFICIE = new Color(0xFCFCFB);
    private static final Color TINTA = new Color(0x0B0B0B);
    private static final Color TINTA_SECUNDARIA = new Color(0x52514E);
    private static final Color CUADRICULA = new Color(0xE1E0D9);
    private static final Color EJE = new Color(0xC3C2B7);
    private static final Color SERIE = new Color(0x2A78D6);
    private static final Color SERIE_TRANSLUCIDA = new Color(0x2A, 0x78, 0xD6, 140);

    @Override
    public Path graficarSecuencia(List<Observacion> observaciones, String titulo, Path ruta) throws IOException {
        Lienzo lienzo = new Lienzo(1500, 820, titulo, "Las " + observaciones.size() + " observaciones",
                "n", "U(n)", 0, observaciones.size(), 0, 1);
        for (Observacion obs : observaciones) {
            lienzo.punto(obs.n(), obs.u());
        }
        return lienzo.guardar(ruta);
    }

    @Override
    public Path graficarHistograma(ResumenEstadistico resumen, String titulo, Path ruta) throws IOException {
        List<Integer> frecuencias = resumen.frecuencias();
        int k = frecuencias.size();
        double esperada = (double) resumen.cantidad() / k;
        String subtitulo = "Chi-cuadrado = " + FormatoDecimal.formatear(resumen.chiCuadrado(), 4) + " frente a "
                + resumen.valorCriticoChiCuadrado() + " (alfa = 0.05, 9 g.l.): la uniformidad "
                + (resumen.pasaChiCuadrado() ? "se acepta" : "se rechaza");
        double alturaMaxima = Math.max(Collections.max(frecuencias), esperada) * 1.25;
        Lienzo lienzo = new Lienzo(1350, 800, titulo, subtitulo, "Intervalo de U(n)", "Frecuencia",
                0, 1, 0, alturaMaxima);
        for (int i = 0; i < k; i++) {
            lienzo.barra((double) i / k, (double) (i + 1) / k, frecuencias.get(i));
        }
        lienzo.lineaHorizontal(esperada);
        lienzo.entradaLeyenda("Frecuencia esperada (" + Math.round(esperada) + ")", TINTA, true);
        lienzo.entradaLeyenda("Frecuencia observada", SERIE, false);
        return lienzo.guardar(ruta);
    }

    @Override
    public Path graficarDispersion(List<Observacion> observaciones, String titulo, Path ruta) throws IOException {
        Lienzo lienzo = new Lienzo(1000, 1060, titulo, (observaciones.size() - 1) + " pares consecutivos",
                "U(n)", "U(n+1)", 0, 1, 0, 1);
        // Cada punto es el par (U(n), U(n+1)); patrones visibles indicarían dependencia.
        for (int i = 0; i + 1 < observaciones.size(); i++) {
            lienzo.punto(observaciones.get(i).u(), observaciones.get(i + 1).u());
        }
        return lienzo.guardar(ruta);
    }

    /** Área de dibujo con ejes, cuadrícula y escalas lineales; encapsula los detalles de Java2D. */
    private static final class Lienzo {

        private static final Font FUENTE_TITULO = new Font(Font.SANS_SERIF, Font.BOLD, 30);
        private static final Font FUENTE_SUBTITULO = new Font(Font.SANS_SERIF, Font.PLAIN, 22);
        private static final Font FUENTE_TEXTO = new Font(Font.SANS_SERIF, Font.PLAIN, 19);

        private final BufferedImage imagen;
        private final Graphics2D g;
        private final double xMin;
        private final double xMax;
        private final double yMin;
        private final double yMax;
        // Bordes del área de datos, en píxeles.
        private final double izquierda = 100;
        private final double derecha;
        private final double arriba = 120;
        private final double abajo;
        private double xLeyenda;

        Lienzo(int ancho, int alto, String titulo, String subtitulo, String etiquetaX, String etiquetaY,
               double xMin, double xMax, double yMin, double yMax) {
            this.xMin = xMin;
            this.xMax = xMax;
            this.yMin = yMin;
            this.yMax = yMax;
            this.derecha = ancho - 40;
            this.abajo = alto - 90;
            this.xLeyenda = izquierda + 16;
            imagen = new BufferedImage(ancho, alto, BufferedImage.TYPE_INT_RGB);
            g = imagen.createGraphics();
            g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
            g.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
            g.setColor(SUPERFICIE);
            g.fillRect(0, 0, ancho, alto);
            dibujarTitulos(titulo, subtitulo);
            dibujarEjes(etiquetaX, etiquetaY);
        }

        /** Convierte un valor de datos en coordenada horizontal de la imagen. */
        private double px(double x) {
            return izquierda + (x - xMin) / (xMax - xMin) * (derecha - izquierda);
        }

        /** Convierte un valor de datos en coordenada vertical (en la imagen, y crece hacia abajo). */
        private double py(double y) {
            return abajo - (y - yMin) / (yMax - yMin) * (abajo - arriba);
        }

        void punto(double x, double y) {
            g.setColor(SERIE_TRANSLUCIDA);
            g.fill(new Ellipse2D.Double(px(x) - 2, py(y) - 2, 4, 4));
        }

        /** Barra desde la línea base hasta {@code valor}, con su cifra escrita dentro en blanco. */
        void barra(double desde, double hasta, int valor) {
            double x0 = px(desde) + 1; // 1 px por lado: 2 px de separación entre barras vecinas
            double x1 = px(hasta) - 1;
            double y0 = py(valor);
            double y1 = py(0);
            g.setColor(SERIE);
            g.fill(new Rectangle2D.Double(x0, y0, x1 - x0, y1 - y0));
            g.setColor(Color.WHITE);
            g.setFont(FUENTE_TEXTO);
            FontMetrics medidas = g.getFontMetrics();
            String texto = String.valueOf(valor);
            g.drawString(texto, (float) ((x0 + x1 - medidas.stringWidth(texto)) / 2),
                    (float) ((y0 + y1 + medidas.getAscent()) / 2 - 2));
        }

        void lineaHorizontal(double y) {
            g.setColor(TINTA);
            g.setStroke(new BasicStroke(2f));
            g.draw(new Line2D.Double(izquierda, py(y), derecha, py(y)));
        }

        /** Agrega una entrada a la leyenda (línea o recuadro de color seguido de su texto). */
        void entradaLeyenda(String texto, Color color, boolean comoLinea) {
            double y = arriba + 24;
            g.setColor(color);
            if (comoLinea) {
                g.setStroke(new BasicStroke(2f));
                g.draw(new Line2D.Double(xLeyenda, y, xLeyenda + 28, y));
            } else {
                g.fill(new Rectangle2D.Double(xLeyenda + 4, y - 9, 20, 18));
            }
            g.setColor(TINTA_SECUNDARIA);
            g.setFont(FUENTE_TEXTO);
            g.drawString(texto, (float) (xLeyenda + 38), (float) (y + 7));
            xLeyenda += 38 + g.getFontMetrics().stringWidth(texto) + 36;
        }

        Path guardar(Path ruta) throws IOException {
            g.dispose();
            Path carpeta = ruta.toAbsolutePath().getParent();
            if (carpeta != null) {
                Files.createDirectories(carpeta);
            }
            ImageIO.write(imagen, "png", ruta.toFile());
            return ruta;
        }

        private void dibujarTitulos(String titulo, String subtitulo) {
            g.setColor(TINTA);
            g.setFont(FUENTE_TITULO);
            g.drawString(titulo, (float) izquierda, 48f);
            g.setColor(TINTA_SECUNDARIA);
            g.setFont(FUENTE_SUBTITULO);
            g.drawString(subtitulo, (float) izquierda, 86f);
        }

        /** Cuadrícula fina, marcas con valores "redondos", ejes y sus etiquetas. */
        private void dibujarEjes(String etiquetaX, String etiquetaY) {
            g.setFont(FUENTE_TEXTO);
            FontMetrics medidas = g.getFontMetrics();
            g.setStroke(new BasicStroke(1f));

            double pasoX = pasoRedondo(xMax - xMin);
            for (long i = (long) Math.ceil(xMin / pasoX); i * pasoX <= xMax + 1e-9; i++) {
                double x = px(i * pasoX);
                String texto = textoMarca(i * pasoX, pasoX);
                g.setColor(CUADRICULA);
                g.draw(new Line2D.Double(x, arriba, x, abajo));
                g.setColor(TINTA_SECUNDARIA);
                g.drawString(texto, (float) (x - medidas.stringWidth(texto) / 2.0), (float) (abajo + 12 + medidas.getAscent()));
            }
            double pasoY = pasoRedondo(yMax - yMin);
            for (long i = (long) Math.ceil(yMin / pasoY); i * pasoY <= yMax + 1e-9; i++) {
                double y = py(i * pasoY);
                String texto = textoMarca(i * pasoY, pasoY);
                g.setColor(CUADRICULA);
                g.draw(new Line2D.Double(izquierda, y, derecha, y));
                g.setColor(TINTA_SECUNDARIA);
                g.drawString(texto, (float) (izquierda - 12 - medidas.stringWidth(texto)), (float) (y + medidas.getAscent() / 2.0 - 3));
            }

            g.setColor(EJE);
            g.setStroke(new BasicStroke(1.5f));
            g.draw(new Line2D.Double(izquierda, abajo, derecha, abajo));
            g.draw(new Line2D.Double(izquierda, arriba, izquierda, abajo));

            g.setColor(TINTA_SECUNDARIA);
            g.drawString(etiquetaX, (float) ((izquierda + derecha - medidas.stringWidth(etiquetaX)) / 2),
                    (float) (abajo + 70));
            // Etiqueta del eje Y escrita en vertical: se rota el sistema de coordenadas 90 grados.
            AffineTransform original = g.getTransform();
            g.rotate(-Math.PI / 2);
            g.drawString(etiquetaY, (float) (-(arriba + abajo + medidas.stringWidth(etiquetaY)) / 2), 30f);
            g.setTransform(original);
        }

        /** Paso entre marcas de 1, 2 o 5 por una potencia de 10, para unas 5 divisiones. */
        private static double pasoRedondo(double rango) {
            double bruto = rango / 5;
            double magnitud = Math.pow(10, Math.floor(Math.log10(bruto)));
            double normalizado = bruto / magnitud;
            double factor = normalizado < 1.5 ? 1 : normalizado < 3 ? 2 : normalizado < 7 ? 5 : 10;
            return factor * magnitud;
        }

        /** Texto de una marca con los decimales justos para el tamaño del paso. */
        private static String textoMarca(double valor, double paso) {
            int decimales = paso >= 1 ? 0 : (int) Math.ceil(-Math.log10(paso) - 1e-9);
            return FormatoDecimal.formatear(valor, decimales);
        }
    }
}
