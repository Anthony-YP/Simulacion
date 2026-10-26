package model;

/** Pesos del índice I = wH*H + wN*N + wT*Tf. Deben sumar 1. */
public record PesosModelo(String nombre, double wHumedad, double wNubosidad, double wTemperatura) {

    public PesosModelo {
        double total = wHumedad + wNubosidad + wTemperatura;
        if (Math.abs(total - 1.0) > 1e-9) {
            throw new IllegalArgumentException("Los pesos deben sumar 1 y suman " + total);
        }
    }

    /** Modelo original de la guía: I = 0.5H + 0.3N + 0.2Tf. */
    public static final PesosModelo ORIGINAL = new PesosModelo("Original", 0.50, 0.30, 0.20);

    /** Modelo ajustado: más peso a la nubosidad, menos a la temperatura. */
    public static final PesosModelo AJUSTADO = new PesosModelo("Ajustado", 0.45, 0.40, 0.15);
}
