# Apuntes-Actividades-IA
Repositorio de apuntes, Alberto Vilchez Hurtado, actividades y proyectos de la materia de IA.
---

## Actividad Modelado de una Red Neuronal para la Detección de Emociones

En esta actividad, se busca modelar una red neuronal que pueda identificar emociones a través de los valores obtenidos de los landmarks que genera mediapipe.

### *Instrucciones*

- Definir el tipo de red neuronal y describir cada una de sus partes.
- Definir los patrones a utilizar.
- Definir que funcion de activacion es necesaria para este problema.
- Definir el numero máximo de entradas.
- ¿Que valores a la salida de la red se podrian esperar?
- ¿Cuales son los valores maximos que puede tener el bias?

### **Definir el Tipo de Red Neuronal**

Se utilizará una **red neuronal artificial (ANN)** compuesta por capas densas. Esta consiste en una red de nodos interconectados (neuronas artificiales)

1. **Capa de entrada:** Recibe los valores de los landmarks procesados (coordenadas normalizadas o relaciones geométricas relevantes).

2. **Capas ocultas:** Se utilizan varias capas densas con funciones de activación adecuadas para extraer patrones de las relaciones entre puntos faciales.

3. **Capa de salida:** Devuelve la emoción detectada como una clasificación entre tristeza, enojo, sorpresa y felicidad.

### **Definición de los Patrones a Utilizar**

Los patrones serán los valores numéricos obtenidos de los landmarks faciales:

- **Índices faciales:** Índices faciales para expresiones.
    ```python
    BOCA_IZQUIERDA = 61
    BOCA_DERECHA = 291
    BOCA_SUPERIOR = 13
    BOCA_INFERIOR = 14
    CEJA_IZQUIERDA = 21
    CEJA_DERECHA = 22
    PARPADO_SUPERIOR = 159
    PARPADO_INFERIOR = 145
- **Distancias clave:** Entre cejas, párpados, boca y comisuras.
- **Proporciones:** Relación ancho/alto de la boca y ojos.
- **Desplazamiento entre frames:** Para verificar actividad y prevenir falsos positivos con imágenes estáticas.

### **Función de Activación Necesaria**

- **ReLU (Rectified Linear Unit):** Para las capas ocultas, ya que este mejora la convergencia en redes profundas.
- **Softmax:** En la capa de salida para clasificar las emociones en categorías discretas.

### **Número Máximo de Entradas**

El número de entradas dependerá de la cantidad de landmarks procesados. Por ejemplo:

Ancho y alto de la boca: 2 entradas.

Distancia entre las cejas: 1 entrada.

Distancia entre los párpados: 1 entrada.

Posición de las comisuras de la boca: 1 entrada.

Desplazamiento entre frames (si decides incluirlo): 1 entrada.

### **¿Que valores a la salida de la red se podrian esperar?**

Estos serian las categorías de emociones que deseamos detectar. Según el modelo y las emociones que estámos tratando de clasificar (tristeza, enojo, sorpresa y felicidad)
Landmarks Faciales: Los landmarks faciales son puntos de referencia en la cara que MediaPipe detecta. Cada punto tiene coordenadas (x, y, z), donde:

- Los landmarks faciales incluyen puntos clave para áreas como:
- Cejas
- Ojos
- Nariz
- Boca
- Comisuras de la boca
- Mandíbula

MediaPipe usa 468 puntos de referencia en total, pero para un análisis de emociones basado en expresiones faciales, es posible que utilices solo una parte de esos puntos clave.

**Distancias entre Landmarks:** Puedes calcular distancias entre diferentes puntos faciales, lo que puede ser crucial para la detección de emociones como tristeza, enojo, sorpresa y felicidad. Algunos ejemplos de distancias clave que podrías medir incluyen:

- Distancia entre las cejas: Para detectar enojo, si las cejas están muy cerca una de la otra.

- Distancia entre los párpados: Para detectar sorpresa, si los ojos están muy abiertos.

- Distancia entre las comisuras de la boca: Para detectar una sonrisa (felicidad) o boca fruncida (tristeza).

- Relación de ancho y alto de la boca y ojos: Esto ayuda a detectar si la persona está sonriendo o sorprendida.

- Proporciones Faciales: Puedes utilizar las proporciones entre diferentes puntos para describir características faciales específicas. Algunas proporciones pueden ser:

- Ancho de la boca / Altura de la boca: Relacionado con la sonrisa (felicidad).

- Distancia entre los ojos / Distancia entre los párpados: Relacionado con la sorpresa, si la distancia es mayor, se puede indicar sorpresa.

- Distancia entre las comisuras de la boca / Altura de la cara: Puede ayudar a medir la intensidad de una sonrisa o fruncimiento de labios.

**Desplazamiento entre Frames:** Se puede medir el movimiento de los puntos faciales entre diferentes frames de video, lo que puede ayudar a diferenciar emociones estáticas de emociones más dinámicas. Esto es útil para: **Prevenir falsos positivos: Asegurando que una emoción detectada esté basada en un cambio genuino de expresión en lugar de ser simplemente una imagen estática.**

#### Ejemplos de valores medibles:
Landmarks de la boca (por ejemplo, puntos 61 a 67 de MediaPipe):
Medir la distancia entre las comisuras de la boca podría indicar si la persona está sonriendo (felicidad).

Landmarks de las cejas (por ejemplo, puntos 33 a 50):
La distancia entre las cejas puede indicar enojo si están muy cercanas o sorprendidas si están muy abiertas.

Landmarks de los ojos (por ejemplo, puntos 47 a 50):
La apertura de los ojos puede ser una medida de sorpresa si los ojos están muy abiertos.

Relación entre la altura y el ancho de la boca y los ojos:
Estos valores pueden ser útiles para determinar la intensidad de las emociones.

### **Valores Máximos del Bias**

No se sabe, ya que cada iteracion es diferente y las epocas cambian.