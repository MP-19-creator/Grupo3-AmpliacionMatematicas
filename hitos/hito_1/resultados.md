RESULTADOS AL ESTUDIAR ORBITAS DE KEPLER CON METODOS EULER RK4 Y CN SIN FUNCIONES:

Al cambiar el dt se ve claro que cada método se comporta de forma distinta con Euler si usamos un dt grande la órbita se va deformando y acaba alejándose de la trayectoria circular que debería ser. Si hacemos dt más pequeño, el resultado mejora bastante.

Con Crank-Nicolson la órbita se mantiene bastante mejor y el error es menor que con Euler. Al reducir el dt la trayectoria se acerca todavía más a la solución esperada.

RK4 es el método que mejor funciona de los tres. Aunque uses un dt grande la órbita sale bastante bien y al hacerlo más pequeño apenas se nota diferencia.

En general cuanto menor es dt más precisa es la solución, Aunque hay mucha diferencia entre un metodo de un orden u otro.