package model;

/** Una fila de la tabla final que pide la guía. */
public record ResultadoHora(String hora, double humedad, double nubosidad, double temperatura,
                            double h, double n, double tf, double indice, String estado) {
}
