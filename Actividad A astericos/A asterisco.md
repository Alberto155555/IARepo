# Apuntes-Actividades-IA
Repositorio de apuntes, Alberto Vilchez Hurtado, actividades y proyectos de la materia de IA.
## 1.- Actividad de redes neuronales 1

En esta actividad, se busca modelar un tipo de red neuronal que pueda jugar al 5 en linea sub gravedad en un tablero de 20*20.
#### *Instrucciones*
    Modelar una red neuronal que pueda jugar al 5 en linea sin gravedad en un tablero 20x20 
        Definir el tipo de red neuronal y describir cada  una de sus partes
        Definir los patrones a utilizar
        Definir funciones de activación es necesaria para este problema
        Definir el numero maximo de entradas.
        ¿Que valores a la salida de la red se podrian esperar?

#### *tipo de red neuronal y cada  una de sus partes*
    Sera una red neuronal convolucional ya que se necesita de un tablero de juegos
    una zona de juego de 20x20 
    fichas A y B 
    limites de la zona
    


#### *patrones a utilizar*
    entran en un formato tipo vector
    Líneas de fichas consecutivas para ver si tenemos alguna posible
    fichas contrarias cercanas
    lineas que puedan juntarse o esten en la misma direccion
    Esquinas y bordes para evitar posibles bloqueos
    Patrones defensivos y ofensivos para protejer mis lineas y impedir las del oponente

#### *funciones de activación*
    Softmax, ya que es una función de activación que nos va a decir a partir de los datos de entrada en una multiclase 
    cuando si es, tiende a 1 cuando no conoce tiende a 0

#### *numero maximo de entradas*
    -400 entradas del 20x20 por los canales
    - 1 pertenece al jugador
    - 0 pertenece al oponente

#### *Respuestas*
    ¿Que valores a la salida de la red se podrian esperar?
    Dependiendo el tiro
    ¿Cuales son los valores maximos que puede tener el bias?
    No se sabe, ya que cada iteracion es diferente y las epocas cambian.

    
### Recursos Adicionales

- ![Gráfico de la Actividad](act1.jpg)
-  ![Gráfico de la Actividad](act1.1.jpg)
