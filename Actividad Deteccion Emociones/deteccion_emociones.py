import cv2
import mediapipe as mp
import numpy as np
import time

# Inicializar MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh 
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1,
                                  min_detection_confidence=0.5, min_tracking_confidence=0.5)

cap = cv2.VideoCapture(0)

prev_landmarks = None
last_movement_time = time.time()

MOVEMENT_THRESHOLD = 1.0  # Más sensible
NO_MOVEMENT_DURATION = 1  # Menos tolerante

# Índices faciales para expresiones
BOCA_IZQUIERDA = 61
BOCA_DERECHA = 291
BOCA_SUPERIOR = 13
BOCA_INFERIOR = 14
CEJA_IZQUIERDA = 21
CEJA_DERECHA = 22
PARPADO_SUPERIOR = 159
PARPADO_INFERIOR = 145

def calcular_distancia(a, b):
    return np.linalg.norm(np.array(a) - np.array(b))

def detectar_sonrisa(landmarks):
    izquierda = landmarks[BOCA_IZQUIERDA]
    derecha = landmarks[BOCA_DERECHA]
    superior = landmarks[BOCA_SUPERIOR]
    inferior = landmarks[BOCA_INFERIOR]

    ancho_boca = calcular_distancia(izquierda, derecha)
    alto_boca = calcular_distancia(superior, inferior)

    ratio = ancho_boca / alto_boca if alto_boca != 0 else 0
    return ratio > 1.0

def detectar_enojo(landmarks):
    ceja_izq = landmarks[CEJA_IZQUIERDA]
    ceja_der = landmarks[CEJA_DERECHA]
    return calcular_distancia(ceja_izq, ceja_der) < 70

def detectar_tristeza(landmarks):
    izquierda = landmarks[BOCA_IZQUIERDA]
    derecha = landmarks[BOCA_DERECHA]
    superior = landmarks[BOCA_SUPERIOR]
    return izquierda[1] > superior[1] and derecha[1] > superior[1]

def detectar_sorpresa(landmarks):
    superior = landmarks[BOCA_SUPERIOR]
    inferior = landmarks[BOCA_INFERIOR]
    ojo_superior = landmarks[PARPADO_SUPERIOR]
    ojo_inferior = landmarks[PARPADO_INFERIOR]

    boca_abierta = calcular_distancia(superior, inferior) > 18
    ojo_abierto = calcular_distancia(ojo_superior, ojo_inferior) > 6
    return boca_abierta and ojo_abierto

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            current_landmarks = []
            h, w, _ = frame.shape
            puntos = {}

            for idx, lm in enumerate(face_landmarks.landmark):
                x, y = int(lm.x * w), int(lm.y * h)
                current_landmarks.append((x, y))
                puntos[idx] = (x, y)
                cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

            if prev_landmarks:
                diffs = [calcular_distancia(a, b) for a, b in zip(prev_landmarks, current_landmarks)]
                avg_movement = np.mean(diffs)

                if avg_movement > MOVEMENT_THRESHOLD:
                    last_movement_time = time.time()

                cv2.putText(frame, f"Mov: {avg_movement:.2f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

            prev_landmarks = current_landmarks

            emocion_actual = "Ninguna"

            if detectar_sorpresa(puntos):
                emocion_actual = "Sorpresa"
            elif detectar_enojo(puntos):
                emocion_actual = "Enojo"
            elif detectar_tristeza(puntos):
                emocion_actual = "Tristeza"
            elif detectar_sonrisa(puntos):
                emocion_actual = "Sonrisa"

            if time.time() - last_movement_time > NO_MOVEMENT_DURATION or emocion_actual == "Ninguna":
                cv2.putText(frame, "IMAGEN", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                cv2.putText(frame, "Persona", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 0), 2)

            cv2.putText(frame, f"Emocion: {emocion_actual}", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    cv2.imshow('Verificacion de Vida con Expresiones', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
