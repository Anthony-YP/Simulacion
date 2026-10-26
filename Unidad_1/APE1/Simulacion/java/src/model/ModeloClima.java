package model;

import java.util.ArrayList;
import java.util.List;

/**
 * MODELO - Índice de posibilidad de lluvia (misma lógica que la versión Python).
 */
public class ModeloClima {

    // PASO 1 - Datos de entrada (tabla de la guía)
    public static final List<Medicion> DATOS_GUIA = List.of(
            new Medicion("06:00", 65, 40, 14),
            new Medicion("08:00", 70, 50, 16),
            new Medicion("10:00", 68, 45, 18),
            new Medicion("12:00", 60, 30, 22),
            new Medicion("14:00", 75, 70, 20),
            new Medicion("16:00", 85, 85, 18),
            new Medicion("18:00", 92, 95, 16),
            new Medicion("20:00", 88, 90, 17),
            new Medicion("22:00", 80, 75, 15));

    // PASO 2 - Normalización: 90 % -> 0.90
    public static double normalizar(double porcentaje) {
        return porcentaje / 100.0;
    }

    // PASO 3 - Factor de temperatura: recta Tf = 1 - 0.05(T - 10) limitada a [0.10, 1.00]
    public static double factorTemperatura(double temperatura) {
        double tf = 1.0 - 0.05 * (temperatura - 10.0);
        return Math.max(0.10, Math.min(1.00, tf));
    }

    // PASO 4 - Ecuación del modelo
    public static double indiceLluvia(double h, double n, double tf, PesosModelo p) {
        return p.wHumedad() * h + p.wNubosidad() * n + p.wTemperatura() * tf;
    }

    // PASO 5 - Tabla de reglas
    public static String clasificar(double indice) {
        if (indice < 0.40) return "Sin lluvia";
        if (indice < 0.60) return "Baja posibilidad";
        if (indice < 0.75) return "Lluvia probable";
        return "Lluvia";
    }

    // PASO 6 - Simular todas las horas
    public static List<ResultadoHora> simular(List<Medicion> datos, PesosModelo pesos) {
        List<ResultadoHora> resultados = new ArrayList<>();
        for (Medicion m : datos) {
            double h = normalizar(m.humedad());
            double n = normalizar(m.nubosidad());
            double tf = factorTemperatura(m.temperatura());
            double i = Math.round(indiceLluvia(h, n, tf, pesos) * 10000.0) / 10000.0;
            resultados.add(new ResultadoHora(m.hora(), m.humedad(), m.nubosidad(),
                    m.temperatura(), h, n, tf, i, clasificar(i)));
        }
        return resultados;
    }
}
