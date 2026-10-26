package model;

/** Una fila de datos medidos: hora, humedad %, nubosidad % y temperatura °C. */
public record Medicion(String hora, double humedad, double nubosidad, double temperatura) {
}
