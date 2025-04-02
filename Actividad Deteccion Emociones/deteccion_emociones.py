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

# Índices para boca (landmarks comunes en MediaPipe)
LEFT_MOUTH = 61
RIGHT_MOUTH = 291
TOP_MOUTH = 13
BOTTOM_MOUTH = 14

def calcular_distancia(a, b):
    return np.linalg.norm(np.array(a) - np.array(b))

def detectar_sonrisa(landmarks):
    """Detecta sonrisa con relación ancho/alto de la boca."""
    left = landmarks[LEFT_MOUTH]
    right = landmarks[RIGHT_MOUTH]
    top = landmarks[TOP_MOUTH]
    bottom = landmarks[BOTTOM_MOUTH]

    ancho_boca = calcular_distancia(left, right)
    alto_boca = calcular_distancia(top, bottom)

    ratio = ancho_boca / alto_boca if alto_boca != 0 else 0

    return ratio > 2  # Umbral aproximado de sonrisa

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
            points = {}

            for idx, lm in enumerate(face_landmarks.landmark):
                x, y = int(lm.x * w), int(lm.y * h)
                current_landmarks.append((x, y))
                points[idx] = (x, y)
                cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

            if prev_landmarks:
                diffs = [calcular_distancia(a, b) for a, b in zip(prev_landmarks, current_landmarks)]
                avg_movement = np.mean(diffs)

                if avg_movement > MOVEMENT_THRESHOLD:
                    last_movement_time = time.time()

                cv2.putText(frame, f"Mov: {avg_movement:.2f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

            prev_landmarks = current_landmarks

            sonrisa = detectar_sonrisa(points)

            if time.time() - last_movement_time > NO_MOVEMENT_DURATION or not sonrisa:
                cv2.putText(frame, "IMAGEN", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                cv2.putText(frame, "Persona", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 0), 2)
                cv2.putText(frame, "Sonrisa", (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    cv2.imshow('Verificacion de Vida con Sonrisa', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
