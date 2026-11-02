# GUI de ORBITA

Ejecutar desde la raiz del repositorio:

```powershell
python PEI1/PEI1.py
```

El flujo esta coordinado en `PEI1/PEI1.py`:

1. Crea la GUI y conecta las acciones de sus controles.
2. Recibe los parametros elegidos por el usuario.
3. Prepara la funcion fisica F y la condicion inicial U0.
4. Llama a los calculos del motor pasandoles F, U0 y el metodo.
5. Entrega los resultados a la GUI para que dibuje.

La GUI no importa el motor ni la fisica. Sus paginas dibujan los datos recibidos:
movimiento, conservacion, estabilidad y precision. Los calculos que antes estaban
en esas paginas estan ahora en el principal. No hay un modulo intermedio nuevo.

En `iniciar_programa()`, la llamada `interfaz["solicitar_calculo"]()` inicia el primer calculo.
Esta avisa a `calcular_simulacion()`, definida en el principal. Desde alli se llega a
`Cauchy_problem(F, t, U0, metodo)` y a su bucle `for n in range(N)`.
Cada iteracion obtiene U[n+1] a partir de U[n].

Despues, `plt.show()` mantiene el bucle de eventos de la ventana.
Al pulsar Calcular se repite el calculo con los nuevos parametros. La animacion
solo recorre resultados ya calculados.

Los campos numericos se aceptan con Intro; los cambios se aplican con Calcular.
Los calculos son sincronos: la ventana espera mientras terminan.

## Como leer el codigo de la GUI

Empieza por `crear_interfaz()` en `gui.py`. Esta organizada en seis bloques:

1. **Acciones:** define las funciones que responderan a los controles. Definirlas no las ejecuta.
2. **Dibujo:** crea las cuatro paginas, las graficas y los textos.
3. **Controles:** crea deslizadores, campos numericos, botones y selectores.
4. **Eventos:** conecta cada control con la funcion que debe ejecutar.
5. **Animacion:** crea el temporizador que recorre la solucion calculada.
6. **Devolucion:** entrega el estado y las acciones al principal.

Por ejemplo, `boton_calcular.on_clicked(solicitar_calculo)` significa:
«cuando se pulse este boton, llama a solicitar_calculo». No calcula al conectar
el boton. El primer calculo lo inicia el principal despues de crear la GUI.

## Flujo al pulsar Calcular

```text
boton_calcular
  solicitar_calculo()
    leer_parametros()            recoge los valores de los controles
    al_calcular(parametros)      avisa a la funcion entregada por el principal
    estado.update(resultado)    guarda los datos que devuelve el principal
    mostrar_pagina(...)         dibuja los resultados
```

`al_calcular` y `al_preparar_pagina` son funciones recibidas del principal.
La GUI las llama sin conocer las ecuaciones ni los algoritmos que ejecutan.

## Las otras acciones

| Accion | Funcion |
|---|---|
| Cambiar un parametro | `marcar_cambios` avisa de que falta pulsar Calcular. |
| Pulsar una pestana | `seleccionar_pestana` llama a `mostrar_pagina`. |
| Tic del temporizador | `avanzar_animacion` llama a `mostrar_instante`. |
| Pausar o reanudar | `pausar_reanudar` cambia el estado de reproduccion. |
| Restablecer | `restablecer_parametros` recupera los valores iniciales y solicita el calculo. |
| Clic en una grafica temporal | `pulsar_grafica` muestra ese instante. |
| Cerrar | `cerrar_interfaz` detiene el temporizador. |

## Estado y paginas

`estado` guarda los resultados y la situacion de la ventana: `pagina_actual`,
`tiempo_actual`, `indice_actual`, `reproduciendo`, `velocidad` y `cambios_pendientes`.
`paginas` contiene los cuatro objetos encargados de dibujar. Cada uno utiliza
los mismos nombres para sus operaciones principales:

- `mostrar(visible)`: muestra u oculta sus elementos.
- `dibujar()`: prepara las graficas completas cuando cambian los datos.
- `dibujar_instante(indice)`: mueve los marcadores y la caja al instante elegido.

`necesita_dibujo` indica que una pagina debe volver a dibujarse con datos nuevos.
La animacion solo actualiza el instante, sin repetir el dibujo completo de las curvas.

Las funciones `crear_deslizador`, `crear_campo_numerico`, `crear_boton` y
`crear_selector` evitan repetir el formato de cada control. Los campos numericos
validan el texto al pulsar Intro; no sustituyen metodos de los widgets.

Los nombres de la biblioteca, como `on_clicked`, `set_data` o `set_visible`,
se conservan porque son llamadas de Matplotlib.
