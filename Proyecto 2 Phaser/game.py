import pygame
import random
import numpy as np
import os
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier

pygame.init()

# Pantalla
w, h = 800, 400
pantalla = pygame.display.set_mode((w, h))
pygame.display.set_caption("Esquivar proyectiles")

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)

# Carga recursos (ajusta paths si necesario)
base_path = os.path.dirname(os.path.abspath(__file__))

jugador_frames = [
    pygame.image.load(os.path.join(base_path, 'assets/sprites/mono_frame_1.png')),
    pygame.image.load(os.path.join(base_path, 'assets/sprites/mono_frame_2.png')),
    pygame.image.load(os.path.join(base_path, 'assets/sprites/mono_frame_3.png')),
    pygame.image.load(os.path.join(base_path, 'assets/sprites/mono_frame_4.png')),
]
bala_img = pygame.image.load(os.path.join(base_path, 'assets/sprites/purple_ball.png'))
fondo_img = pygame.transform.scale(pygame.image.load(os.path.join(base_path, 'assets/game/fondo2.png')), (w, h))
nave_img = pygame.image.load(os.path.join(base_path, 'assets/game/ufo.png'))

# Rectángulos jugador y enemigos
jugador = pygame.Rect(50, h - 100, 32, 48)
plasma = pygame.Rect(w - 50, h - 90, 16, 16)
nave = pygame.Rect(w - 100, h - 100, 64, 64)

# Limites de movimiento horizontal: +/- 150px desde posicion inicial 50
limite_izquierda = max(0, 50 - 150)
limite_derecha = min(w - jugador.width, 50 + 150)

# Ubicación fija para bala vertical y ovni arriba
pos_nave_superior_x = jugador.x + jugador.width // 2 - 32
pos_nave_superior_y = 20
nave_superior_estatica = pygame.Rect(pos_nave_superior_x, pos_nave_superior_y, 64, 64)

bala_vertical = pygame.Rect(
    nave_superior_estatica.x + nave_superior_estatica.width // 2 - 8,
    nave_superior_estatica.y + nave_superior_estatica.height,
    16, 16
)

velocidad_bala_vertical = 5
bala_vertical_disparada = True

# Estados salto
en_salto = False
en_suelo = True
velocidad_vertical = 15
gravedad = 1

pausa = False
fuente = pygame.font.SysFont('Arial', 24)
menu_activo = True
modo_nn = False
modo_arbol = False
modo_KNN = False

registro_saltos = []
registro_movimientos = []

modelo_binario_salto = None
arbol_decision_salto = None
modelo_KNN_salto = None

modelo_binario_mov = None
arbol_decision_mov = None
modelo_KNN_mov = None

accion_horizontal = 1

# Variables para animación y fondo
current_frame = 0
frame_speed = 10
frame_count = 0

fondo_x1 = 0
fondo_x2 = w

# Proyectil horizontal
plasma_activa = False
vel_bala_horizontal_min = -12
vel_bala_horizontal_max = -9
vel_bala_inferior = 0

# Disparo cooldown
cooldown_disparo = 0
intervalo_disparo = 60


def entrenar_modelo_salto(registro_saltos):
    if len(registro_saltos) < 15:
        print(f"[INFO] Pocos datos para entrenar el modelo salto. Datos: {len(registro_saltos)}")
        return None
    datos = np.array(registro_saltos)
    X = datos[:, :6]
    y = datos[:, 6]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    modelo = Sequential([
        Dense(32, input_dim=6, activation='relu'),
        Dense(32, activation='relu'),
        Dense(16, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    modelo.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    modelo.fit(X_train, y_train, epochs=50, batch_size=16, verbose=0)
    loss, accuracy = modelo.evaluate(X_test, y_test, verbose=0)
    print(f"[INFO] Modelo salto entrenado precisión: {accuracy:.4f}")
    return modelo


def entrenar_arbol_salto(registro_saltos):
    if len(registro_saltos) < 15:
        print(f"[INFO] Pocos datos para árbol salto: {len(registro_saltos)}")
        return None
    datos = np.array(registro_saltos)
    X = datos[:, :6]
    y = datos[:, 6]
    arbol = DecisionTreeClassifier(max_depth=6)
    arbol.fit(X, y)
    print(f"[INFO] Árbol salto entrenado con {len(y)} datos")
    return arbol


def entrenar_KNN_salto(registro_saltos, n_neighbors=3):
    if len(registro_saltos) < n_neighbors:
        print(f"[INFO] Pocos datos para KNN salto: {len(registro_saltos)}")
        return None
    datos = np.array(registro_saltos)
    X = datos[:, :6]
    y = datos[:, 6]
    knn = KNeighborsClassifier(n_neighbors=n_neighbors)
    knn.fit(X, y)
    print(f"[INFO] KNN salto entrenado con {len(y)} datos")
    return knn


def decidir_salto(jugador, plasma, vel_bala_predicha, bala_vertical, bala_vertical_activa, modelo, en_salto_, en_suelo_):
    if modelo is None:
        return False, en_suelo_
    distancia_terreno = abs(jugador.x - plasma.x)
    delta_x_aerea = abs(jugador.centerx - bala_vertical.centerx)
    delta_y_aerea = abs(jugador.centery - bala_vertical.centery)
    hay_proyectil_aire = 1 if bala_vertical_activa else 0
    entrada = np.array([[vel_bala_predicha, distancia_terreno, delta_x_aerea, delta_y_aerea, hay_proyectil_aire, jugador.x]], dtype=np.float32)
    resultado_raw = modelo.predict(entrada, verbose=0)[0][0]
    resultado = 1 if resultado_raw > 0.5 else 0
    if resultado == 1 and en_suelo_:
        en_salto_ = True
        en_suelo_ = False
        print(f"[ACTION] Salto IA (prob={resultado_raw:.3f})")
    return en_salto_, en_suelo_


def decidir_salto_arbol(jugador, plasma, vel_bala_predicha, bala_vertical, bala_vertical_activa, arbol, en_salto_, en_suelo_):
    if arbol is None:
        return False, en_suelo_
    distancia_terreno = abs(jugador.x - plasma.x)
    delta_x_aerea = abs(jugador.centerx - bala_vertical.centerx)
    delta_y_aerea = abs(jugador.centery - bala_vertical.centery)
    hay_proyectil_aire = 1 if bala_vertical_activa else 0
    entrada = np.array([[vel_bala_predicha, distancia_terreno, delta_x_aerea, delta_y_aerea, hay_proyectil_aire, jugador.x]])
    pred = arbol.predict(entrada)[0]
    if pred == 1 and en_suelo_:
        en_salto_ = True
        en_suelo_ = False
        print("[ACTION][ÁRBOL] Salto")
    return en_salto_, en_suelo_


def decidir_salto_KNN(jugador, plasma, vel_bala_predicha, bala_vertical, bala_vertical_activa, knn, en_salto_, en_suelo_):
    if knn is None:
        return False, en_suelo_
    distancia_terreno = abs(jugador.x - plasma.x)
    delta_x_aerea = abs(jugador.centerx - bala_vertical.centerx)
    delta_y_aerea = abs(jugador.centery - bala_vertical.centery)
    hay_proyectil_aire = 1 if bala_vertical_activa else 0
    entrada = np.array([[vel_bala_predicha, distancia_terreno, delta_x_aerea, delta_y_aerea, hay_proyectil_aire, jugador.x]])
    pred = knn.predict(entrada)[0]
    if pred == 1 and en_suelo_:
        en_salto_ = True
        en_suelo_ = False
        print("[ACTION][KNN] Salto")
    return en_salto_, en_suelo_


def entrenar_movimiento(registro_movimientos):
    if len(registro_movimientos) < 10:
        print("[INFO] Pocos datos para entrenar movimiento")
        return None
    datos = np.array(registro_movimientos)
    X = datos[:, :8].astype('float32')
    y = datos[:, 8].astype('int')
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    modelo = Sequential([
        Dense(32, input_dim=8, activation='relu'),
        Dense(16, activation='relu'),
        Dense(3, activation='softmax')
    ])
    modelo.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    modelo.fit(X_train, y_train, epochs=50, batch_size=16, verbose=0)
    loss, acc = modelo.evaluate(X_test, y_test, verbose=0)
    print(f"[INFO] Modelo movimiento entrenado precisión: {acc:.4f}")
    return modelo


def entrenar_arbol_movimiento(registro_movimientos):
    if len(registro_movimientos) < 10:
        print("[INFO] Pocos datos para árbol movimiento")
        return None
    datos = np.array(registro_movimientos)
    X = datos[:, :8].astype('float32')
    y = datos[:, 8].astype('int')
    arbol = DecisionTreeClassifier(max_depth=6)
    arbol.fit(X, y)
    print(f"[INFO] Árbol movimiento entrenado con {len(y)} datos")
    return arbol


def entrenar_KNN_movimiento(registro_movimientos, n_neighbors=3):
    if len(registro_movimientos) < n_neighbors:
        print("[INFO] Pocos datos para KNN movimiento")
        return None
    datos = np.array(registro_movimientos)
    X = datos[:, :8].astype('float32')
    y = datos[:, 8].astype('int')
    knn = KNeighborsClassifier(n_neighbors=n_neighbors)
    knn.fit(X, y)
    print(f"[INFO] KNN movimiento entrenado con {len(y)} datos")
    return knn


def decidir_movimiento(jugador, bala_vertical, modelo_mov, en_salto, plasma):
    global accion_horizontal
    if modelo_mov is None:
        return jugador.x, 1
    distancia_proyectil_suelo = abs(jugador.x - plasma.x)
    entrada = np.array([[jugador.x, jugador.y, bala_vertical.centerx, bala_vertical.centery, plasma.x, plasma.y, distancia_proyectil_suelo, 1 if en_salto else 0]], dtype=np.float32)
    salida = modelo_mov.predict(entrada, verbose=0)[0]  # Probabilidades softmax
    clase = np.argmax(salida)
    accion_horizontal = clase
    if clase == 0 and jugador.x > limite_izquierda:
        jugador.x -= 5
        print(f"[ACTION][NN] Mover Izquierda (x={jugador.x})")
    elif clase == 2 and jugador.x < limite_derecha:
        jugador.x += 5
        print(f"[ACTION][NN] Mover Derecha (x={jugador.x})")
    else:
        print(f"[ACTION][NN] Quedarse quieto (x={jugador.x})")

    # Limitar movimiento dentro de rango permitido
    jugador.x = max(limite_izquierda, min(jugador.x, limite_derecha))

    return jugador.x, clase


def decidir_movimiento_arbol(jugador, bala_vertical, arbol_mov, en_salto, plasma):
    global accion_horizontal
    if arbol_mov is None:
        return jugador.x, 1
    distancia_proyectil_suelo = abs(jugador.x - plasma.x)
    entrada = np.array([[jugador.x, jugador.y, bala_vertical.centerx, bala_vertical.centery, plasma.x, plasma.y, distancia_proyectil_suelo, 1 if en_salto else 0]], dtype=np.float32)
    accion = arbol_mov.predict(entrada)[0]
    accion_horizontal = accion
    if accion == 0 and jugador.x > limite_izquierda:
        jugador.x -= 5
        print(f"[ACTION][ÁRBOL] Mover Izquierda (x={jugador.x})")
    elif accion == 2 and jugador.x < limite_derecha:
        jugador.x += 5
        print(f"[ACTION][ÁRBOL] Mover Derecha (x={jugador.x})")
    else:
        print(f"[ACTION][ÁRBOL] Quedarse quieto (x={jugador.x})")

    jugador.x = max(limite_izquierda, min(jugador.x, limite_derecha))

    return jugador.x, accion


def decidir_movimiento_KNN(jugador, bala_vertical, knn_mov, en_salto, plasma):
    global accion_horizontal
    if knn_mov is None:
        return jugador.x, 1
    distancia_proyectil_suelo = abs(jugador.x - plasma.x)
    entrada = np.array([[jugador.x, jugador.y, bala_vertical.centerx, bala_vertical.centery, plasma.x, plasma.y, distancia_proyectil_suelo, 1 if en_salto else 0]], dtype=np.float32)
    accion = knn_mov.predict(entrada)[0]
    accion_horizontal = accion
    if accion == 0 and jugador.x > limite_izquierda:
        jugador.x -= 5
        print(f"[ACTION][KNN] Mover Izquierda (x={jugador.x})")
    elif accion == 2 and jugador.x < limite_derecha:
        jugador.x += 5
        print(f"[ACTION][KNN] Mover Derecha (x={jugador.x})")
    else:
        print(f"[ACTION][KNN] Quedarse quieto (x={jugador.x})")

    jugador.x = max(limite_izquierda, min(jugador.x, limite_derecha))

    return jugador.x, accion


def manejar_salto():
    global jugador, en_salto, en_suelo, velocidad_vertical, gravedad
    if en_salto:
        jugador.y -= velocidad_vertical
        velocidad_vertical -= gravedad
        if jugador.y >= h - 100:
            jugador.y = h - 100
            en_salto = False
            en_suelo = True
            velocidad_vertical = 15


def guardar_datos():
    global jugador, plasma, vel_bala_inferior, en_salto, bala_vertical_disparada, bala_vertical
    distancia_terreno = abs(jugador.x - plasma.x)
    salto_realizado = 1 if en_salto else 0
    delta_x_aerea = abs(jugador.centerx - bala_vertical.centerx)
    delta_y_aerea = abs(jugador.centery - bala_vertical.centery)
    hay_proyectil_aire = 1 if bala_vertical_disparada else 0
    registro_saltos.append((
        vel_bala_inferior,
        distancia_terreno,
        delta_x_aerea,
        delta_y_aerea,
        hay_proyectil_aire,
        jugador.x,
        salto_realizado
    ))
    distancia_proyectil_suelo = abs(jugador.x - plasma.x)
    registro_movimientos.append((
        jugador.x,
        jugador.y,
        bala_vertical.centerx,
        bala_vertical.centery,
        plasma.x,
        plasma.y,
        distancia_proyectil_suelo,
        1 if en_salto else 0,
        accion_horizontal
    ))


def reset_juego():
    global jugador, plasma, bala_vertical, en_salto, en_suelo, plasma_activa, bala_vertical_disparada, accion_horizontal, menu_activo, velocidad_vertical
    jugador.x, jugador.y = 50, h - 100
    plasma.x = w - 50
    plasma_activa = False
    # Actualizar posición del ovni superior acorde al jugador inicial
    global nave_superior_estatica
    pos_nave_superior_x = jugador.x + jugador.width // 2 - 32
    nave_superior_estatica.x = pos_nave_superior_x
    bala_vertical.x = nave_superior_estatica.x + nave_superior_estatica.width // 2 - bala_vertical.width // 2
    bala_vertical.y = nave_superior_estatica.y + nave_superior_estatica.height
    bala_vertical_disparada = True
    en_salto = False
    en_suelo = True
    velocidad_vertical = 15
    accion_horizontal = 1
    menu_activo = True


def mostrar_menu():
    global menu_activo, modo_nn, modo_arbol, modo_KNN
    pantalla.fill(NEGRO)
    texto = fuente.render("M: Manual | N: NN | A: Árbol | K: KNN | Q: Salir", True, BLANCO)
    pantalla.blit(texto, (w // 10, h // 2))
    pygame.display.flip()
    while menu_activo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_m:
                    modo_nn = modo_arbol = modo_KNN = False
                    menu_activo = False
                elif evento.key == pygame.K_n:
                    modo_nn = True
                    modo_arbol = modo_KNN = False
                    menu_activo = False
                elif evento.key == pygame.K_a:
                    modo_arbol = True
                    modo_nn = modo_KNN = False
                    menu_activo = False
                elif evento.key == pygame.K_k:
                    modo_KNN = True
                    modo_nn = modo_arbol = False
                    menu_activo = False
                elif evento.key == pygame.K_q:
                    if not (modo_nn or modo_arbol or modo_KNN):
                        guardar_datos()
                    print("Juego terminado")
                    pygame.quit()
                    exit()


def entrenar_modelos_completos():
    global modelo_binario_salto, modelo_binario_mov, arbol_decision_salto, arbol_decision_mov, modelo_KNN_salto, modelo_KNN_mov
    modelo_binario_salto = entrenar_modelo_salto(registro_saltos)
    modelo_binario_mov = entrenar_movimiento(registro_movimientos)
    arbol_decision_salto = entrenar_arbol_salto(registro_saltos)
    arbol_decision_mov = entrenar_arbol_movimiento(registro_movimientos)
    modelo_KNN_salto = entrenar_KNN_salto(registro_saltos)
    modelo_KNN_mov = entrenar_KNN_movimiento(registro_movimientos)


def actualizar_juego():
    global current_frame, frame_count, fondo_x1, fondo_x2

    # Fondo
    fondo_x1 -= 2
    fondo_x2 -= 2
    if fondo_x1 <= -w:
        fondo_x1 = w
    if fondo_x2 <= -w:
        fondo_x2 = w
    pantalla.blit(fondo_img, (fondo_x1, 0))
    pantalla.blit(fondo_img, (fondo_x2, 0))

    # Animar jugador
    global current_frame, frame_count
    frame_count += 1
    if frame_count >= frame_speed:
        current_frame = (current_frame + 1) % len(jugador_frames)
        frame_count = 0
    pantalla.blit(jugador_frames[current_frame], (jugador.x, jugador.y))

    # Nave superior fija (ovni)
    pantalla.blit(nave_img, (nave_superior_estatica.x, nave_superior_estatica.y))

    # Bala horizontal
    if plasma_activa:
        pantalla.blit(bala_img, (plasma.x, plasma.y))
    # Bala vertical
    if bala_vertical_disparada:
        pantalla.blit(bala_img, (bala_vertical.x, bala_vertical.y))


def mover_bala_horizontal():
    global plasma, vel_bala_inferior, plasma_activa, cooldown_disparo
    if plasma_activa:
        plasma.x += vel_bala_inferior
        if plasma.x < 0:
            plasma_activa = False
            cooldown_disparo = intervalo_disparo  # Reiniciar cooldown al desactivar bala
    else:
        if cooldown_disparo > 0:
            cooldown_disparo -= 1
        else:
            plasma.x = nave.x + nave.width // 2 - plasma.width // 2
            plasma.y = nave.y + nave.height // 2 - plasma.height // 2
            vel_bala_inferior = random.randint(vel_bala_horizontal_min, vel_bala_horizontal_max)
            plasma_activa = True


def mover_bala_vertical():
    global bala_vertical, bala_vertical_disparada
    if bala_vertical_disparada:
        bala_vertical.y += velocidad_bala_vertical
        if bala_vertical.y > h:
            # Resetea la bala vertical a la posición fija debajo del ovni
            bala_vertical.x = nave_superior_estatica.x + nave_superior_estatica.width // 2 - bala_vertical.width // 2
            bala_vertical.y = nave_superior_estatica.y + nave_superior_estatica.height
            bala_vertical_disparada = True


def main():
    global en_salto, en_suelo, plasma_activa, bala_vertical_disparada, accion_horizontal, menu_activo, pausa, velocidad_vertical
    reloj = pygame.time.Clock()

    mostrar_menu()

    correr = True
    contador_salto = 0
    intervalo_decidir = 5  # frames entre decisiones IA

    while correr:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                if not (modo_nn or modo_arbol or modo_KNN):
                    guardar_datos()
                correr = False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE and en_suelo and not pausa:
                    en_salto = True
                    en_suelo = False
                    velocidad_vertical = 15
                if evento.key == pygame.K_p:
                    pausa = not pausa
                    print("Pausa activada" if pausa else "Pausa desactivada")
                if evento.key == pygame.K_q:
                    if not (modo_nn or modo_arbol or modo_KNN):
                        guardar_datos()
                    pygame.quit()
                    exit()
                if evento.key == pygame.K_r:
                    reset_juego()
                    mostrar_menu()

        if not pausa:
            mover_bala_horizontal()
            mover_bala_vertical()

            if modo_nn:
                if contador_salto >= intervalo_decidir:
                    en_salto, en_suelo = decidir_salto(
                        jugador, plasma, vel_bala_inferior,
                        bala_vertical, bala_vertical_disparada,
                        modelo_binario_salto, en_salto, en_suelo
                    )
                    contador_salto = 0
                else:
                    contador_salto += 1
                if en_salto:
                    manejar_salto()
                jugador.x, accion_horizontal = decidir_movimiento(
                    jugador, bala_vertical, modelo_binario_mov, en_salto, plasma
                )

            elif modo_arbol:
                if contador_salto >= intervalo_decidir:
                    en_salto, en_suelo = decidir_salto_arbol(
                        jugador, plasma, vel_bala_inferior,
                        bala_vertical, bala_vertical_disparada,
                        arbol_decision_salto, en_salto, en_suelo
                    )
                    contador_salto = 0
                else:
                    contador_salto += 1
                if en_salto:
                    manejar_salto()
                jugador.x, accion_horizontal = decidir_movimiento_arbol(
                    jugador, bala_vertical, arbol_decision_mov, en_salto, plasma
                )

            elif modo_KNN:
                if contador_salto >= intervalo_decidir:
                    en_salto, en_suelo = decidir_salto_KNN(
                        jugador, plasma, vel_bala_inferior,
                        bala_vertical, bala_vertical_disparada,
                        modelo_KNN_salto, en_salto, en_suelo
                    )
                    contador_salto = 0
                else:
                    contador_salto += 1
                if en_salto:
                    manejar_salto()
                jugador.x, accion_horizontal = decidir_movimiento_KNN(
                    jugador, bala_vertical, modelo_KNN_mov, en_salto, plasma
                )

            else:
                # Modo manual
                keys = pygame.key.get_pressed()
                accion_horizontal = 1
                if keys[pygame.K_LEFT] and jugador.x > limite_izquierda:
                    jugador.x -= 5
                    accion_horizontal = 0
                if keys[pygame.K_RIGHT] and jugador.x < limite_derecha:
                    jugador.x += 5
                    accion_horizontal = 2
                if keys[pygame.K_UP] and en_suelo:
                    en_salto = True
                    en_suelo = False
                    velocidad_vertical = 15
                if en_salto:
                    manejar_salto()

                # Guardar datos solo en modo manual
                guardar_datos()

            actualizar_juego()

            # Colisión 
            if jugador.colliderect(plasma) or jugador.colliderect(bala_vertical):
                print("Moriste")
                if not (modo_nn or modo_arbol or modo_KNN):
                    guardar_datos()
                entrenar_modelos_completos()
                reset_juego()
                mostrar_menu()

        pygame.display.flip()
        reloj.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
