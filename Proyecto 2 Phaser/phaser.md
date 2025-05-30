# Apuntes-Actividades-IA  
Repositorio de apuntes, Alberto Vilchez Hurtado, actividades y proyectos de la materia de IA.  
---

## Proyecto 2: Juego de Esquivar Proyectiles con IA en Python y Pygame

En este proyecto se implementa un juego interactivo donde un jugador debe esquivar proyectiles en movimiento, utilizando inteligencia artificial para tomar decisiones de salto y movimiento. Se entrenan y prueban diferentes modelos de aprendizaje automático para controlar el comportamiento del jugador: Redes Neuronales, Árboles de Decisión y K-Nearest Neighbors (KNN).

### **Objetivos del Proyecto**

- Implementar un juego interactivo en Python con Pygame.
- Entrenar modelos de aprendizaje automático para controlar decisiones de salto y movimiento.
- Comparar el rendimiento y comportamiento de distintos modelos:  
  - Árboles de Decisión  
  - Redes Neuronales (Deep Learning)  
  - K-Nearest Neighbors (KNN)
- Recoger datos manualmente para alimentar el entrenamiento de los modelos.
- Visualizar en tiempo real el desempeño de las IAs en el juego.

### **Herramientas y Tecnologías Utilizadas**

- Python  
- Librería Pygame para desarrollo de juegos  
- TensorFlow / Keras para redes neuronales  
- Scikit-learn para árboles de decisión y KNN  
- Numpy para manejo de datos  

---

## **Descripción del Juego y Mecánicas**

El jugador controla un personaje que puede moverse horizontalmente dentro de un rango limitado y saltar para esquivar dos tipos de proyectiles:

- **Proyectil horizontal (plasma):** Disparado desde una nave alienígena que se mueve de derecha a izquierda.
- **Proyectil vertical:** Disparado desde un ovni fijo en la parte superior de la pantalla.

**Controles Manuales:**  
- Flechas izquierda y derecha para moverse.  
- Barra espaciadora para saltar.

**IA:**  
El jugador puede ser controlado por tres modelos distintos o de manera manual, seleccionados desde un menú inicial.

---

## **Modelos de Aprendizaje Automático Implementados**

### 1. Redes Neuronales (Deep Learning)

- Arquitectura con varias capas densas (Dense), activación ReLU y una capa final con activación sigmoide para salto o softmax para movimientos.
- Entrenamiento con datos recolectados durante juego manual, usando función de pérdida `binary_crossentropy` para salto y `sparse_categorical_crossentropy` para movimiento.
- Optimización con Adam.

### 2. Árboles de Decisión

- Clasificadores basados en árboles con profundidad máxima limitada (max_depth=6).
- Entrenamiento con los mismos datos de salto y movimiento que las redes neuronales.

### 3. K-Nearest Neighbors (KNN)

- Clasificador con vecinos más cercanos, usualmente con 3 vecinos (n_neighbors=3).
- Entrenamiento y predicción con los mismos conjuntos de datos.

---

## **Datos de Entrenamiento**

Se registran datos de estado durante el juego manual, almacenando variables relevantes como:

- Velocidad proyectil horizontal  
- Distancia horizontal jugador-plasma  
- Distancia horizontal y vertical jugador-proyectil aéreo  
- Estado de proyectil vertical activo o no  
- Posición del jugador  
- Acción tomada (salto o movimiento horizontal)

Estos datos se usan para entrenar los modelos y predecir la próxima acción durante el modo IA.

---

## **Estados Visuales y Componentes**

- **Jugador:** Animación con múltiples frames para dar vida al personaje.
- **Proyectiles:** Imágenes distintas para el plasma horizontal y la bala vertical.
- **Naves:** Imágenes para la nave enemiga y ovni fijo.
- **Fondo:** Fondo animado desplazándose horizontalmente para sensación de movimiento.
- **Interfaz:** Menú inicial para seleccionar modo de juego (Manual, NN, Árbol, KNN).

---

## **Interacción y Controles**

- **Menu inicial:**  
  - Tecla M: Modo manual  
  - Tecla N: Modo red neuronal  
  - Tecla A: Modo árbol de decisión  
  - Tecla K: Modo KNN  
  - Tecla Q: Salir y guardar datos  

- **Durante juego:**  
  - Flechas izquierda/derecha para mover (en modo manual)  
  - Barra espaciadora para saltar  
  - Tecla P para pausar  
  - Tecla R para reiniciar el juego  

---

## **Funciones Clave del Programa**

- **entrenar_modelo_salto / entrenar_movimiento:**  
  Entrenan modelos de red neuronal para salto y movimiento.

- **entrenar_arbol_salto / entrenar_arbol_movimiento:**  
  Entrenan árboles de decisión.

- **entrenar_KNN_salto / entrenar_KNN_movimiento:**  
  Entrenan modelos KNN.

- **decidir_salto / decidir_movimiento:**  
  Usan los modelos para predecir acciones basadas en el estado actual.

- **manejar_salto:**  
  Controla la física del salto (gravedad, movimiento vertical).

- **guardar_datos:**  
  Registra datos de estado y acciones para entrenamiento.

- **reset_juego / mostrar_menu / actualizar_juego:**  
  Gestión de interfaz y lógica del juego.

---

## **Ejecución y Flujo**

1. Se inicia el programa y aparece el menú para seleccionar modo.  
2. En modo manual, el usuario controla al jugador y se recopilan datos.  
3. Al morir, los datos se usan para entrenar los modelos.  
4. En modos IA, el jugador actúa automáticamente según el modelo seleccionado.  
5. El juego se reinicia automáticamente tras cada muerte para continuar el ciclo de entrenamiento y prueba.

---

## **Preguntas Frecuentes**

- **¿Cómo se recopilan los datos?**  
  Los datos se recolectan solo durante el modo manual, guardando características del entorno y la acción tomada en cada frame.

- **¿Qué tan preciso es cada modelo?**  
  La precisión varía según la cantidad y calidad de datos. Los modelos se evalúan con datos de prueba tras el entrenamiento.

- **¿Qué sucede si el jugador muere?**  
  Se guardan los datos actuales, se entrenan los modelos con los nuevos datos y el juego se reinicia mostrando el menú.

- **¿Por qué usar tres tipos de modelos?**  
  Para comparar la efectividad y comportamiento de distintos enfoques de IA en un mismo entorno.

---

## **Requisitos para Ejecutar**

- Python 3.x  
- Librerías: `pygame`, `numpy`, `tensorflow`, `scikit-learn`  
- Archivos de recursos en `assets/` (sprites, imágenes de fondo)

---