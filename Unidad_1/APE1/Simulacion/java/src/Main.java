import java.nio.file.Path;

import controller.SimulacionController;

/** Punto de entrada: crea el controlador y ejecuta la simulación. */
public class Main {

    public static void main(String[] args) throws Exception {
        System.setProperty("java.awt.headless", "true"); // dibuja PNG sin abrir ventanas
        new SimulacionController(Path.of("resultados")).ejecutar();
    }
}
