package montecarlo.vista;

import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Font;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Locale;

import javax.imageio.ImageIO;

import montecarlo.modelo.MuestraPuntos;

/** Gráfica de dispersión de los puntos de Monte Carlo con Java2D (incluido en el JDK). */
public final class VistaGraficos {

    private static final int LADO = 720;
    private static final int MARGEN = 60;
    private static final Color COLOR_DENTRO = new Color(0x2a78c2);
    private static final Color COLOR_FUERA = new Color(0xe4572e);

    private final Path carpeta;

    public VistaGraficos(Path carpeta) {
        this.carpeta = carpeta;
    }

    public Path graficarPuntos(MuestraPuntos muestra) {
        BufferedImage imagen = new BufferedImage(LADO, LADO + 40, BufferedImage.TYPE_INT_RGB);
        Graphics2D g = imagen.createGraphics();
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        g.setColor(Color.WHITE);
        g.fillRect(0, 0, imagen.getWidth(), imagen.getHeight());

        int area = LADO - 2 * MARGEN;
        int radio = radioPunto(muestra.cantidad());
        for (int i = 0; i < muestra.cantidad(); i++) {
            g.setColor(muestra.dentro()[i] ? COLOR_DENTRO : COLOR_FUERA);
            int px = aPixel(muestra.x()[i], area);
            int py = aPixel(-muestra.y()[i], area); // En pantalla el eje y crece hacia abajo.
            if (radio == 0) {
                g.fillRect(px, py, 1, 1);
            } else {
                g.fillOval(px - radio, py - radio, 2 * radio, 2 * radio);
            }
        }

        g.setColor(Color.BLACK);
        g.setStroke(new BasicStroke(1.8f));
        g.drawRect(MARGEN, MARGEN, area, area);
        g.drawOval(MARGEN, MARGEN, area, area);

        g.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 18));
        g.drawString(String.format(Locale.ROOT, "Monte Carlo (Java) con N = %s puntos  ->  pi = %.5f",
                miles(muestra.cantidad()), muestra.piEstimado()), MARGEN, 38);
        g.setFont(new Font(Font.SANS_SERIF, Font.PLAIN, 15));
        dibujarLeyenda(g, COLOR_DENTRO, "Dentro (Nc = " + miles(muestra.cantidadDentro()) + ")", MARGEN, LADO - 15);
        dibujarLeyenda(g, COLOR_FUERA, "Fuera (" + miles(muestra.cantidad() - muestra.cantidadDentro()) + ")",
                MARGEN + 260, LADO - 15);
        g.dispose();

        return guardar(imagen, "puntos_monte_carlo_n" + muestra.cantidad() + ".png");
    }

    /** Marcadores visibles con N pequeño; con N grande, 1 píxel por punto (radio 0) para que no se tapen. */
    private static int radioPunto(int nPuntos) {
        if (nPuntos <= 2_000) {
            return 3;
        }
        return nPuntos <= 20_000 ? 1 : 0;
    }

    /** Convierte una coordenada de [-1, 1] a píxeles dentro del área del cuadrado. */
    private static int aPixel(double valor, int area) {
        return MARGEN + (int) Math.round((valor + 1.0) / 2.0 * area);
    }

    private static void dibujarLeyenda(Graphics2D g, Color color, String texto, int x, int y) {
        g.setColor(color);
        g.fillOval(x, y - 11, 12, 12);
        g.setColor(Color.BLACK);
        g.drawString(texto, x + 20, y);
    }

    private static String miles(long n) {
        return String.format(Locale.ROOT, "%,d", n).replace(',', ' ');
    }

    private Path guardar(BufferedImage imagen, String nombre) {
        Path ruta = carpeta.resolve(nombre);
        try {
            Files.createDirectories(carpeta);
            ImageIO.write(imagen, "png", ruta.toFile());
        } catch (IOException e) {
            throw new UncheckedIOException("No se pudo guardar " + ruta, e);
        }
        return ruta;
    }
}
