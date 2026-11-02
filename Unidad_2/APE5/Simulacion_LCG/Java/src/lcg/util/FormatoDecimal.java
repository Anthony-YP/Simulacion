package lcg.util;

import java.math.BigDecimal;
import java.math.RoundingMode;

/**
 * Formato de números decimales idéntico al de Python ({@code f"{valor:.Nf}"}).
 *
 * <p>No se usa {@code String.format("%.10f")} porque Java redondea "hacia arriba"
 * (HALF_UP) a partir de la representación decimal corta del número, mientras que
 * Python redondea "al par" (HALF_EVEN) sobre el valor binario exacto. En los
 * empates, como 0.00048828125 con 10 decimales, ambos lenguajes darían un último
 * dígito distinto. {@link BigDecimal#BigDecimal(double)} conserva el valor binario
 * exacto, así que con HALF_EVEN se obtiene la misma cadena que en Python.
 */
public final class FormatoDecimal {

    private FormatoDecimal() {
    }

    public static String formatear(double valor, int decimales) {
        if (Double.isNaN(valor)) {
            return "nan";
        }
        if (Double.isInfinite(valor)) {
            return valor > 0 ? "inf" : "-inf";
        }
        String texto = new BigDecimal(valor).setScale(decimales, RoundingMode.HALF_EVEN).toPlainString();
        // BigDecimal no tiene "cero negativo"; Python sí conserva el signo (por ejemplo "-0.000000").
        boolean negativo = Math.copySign(1.0, valor) < 0;
        return negativo && !texto.startsWith("-") ? "-" + texto : texto;
    }
}
