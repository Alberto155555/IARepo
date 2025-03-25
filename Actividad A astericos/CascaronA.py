import pygame
import math
import heapq

# Configuraciones iniciales
ANCHO_VENTANA = 800
VENTANA = pygame.display.set_mode((ANCHO_VENTANA, ANCHO_VENTANA))
pygame.display.set_caption("Visualización de Nodos")

# Colores (RGB)
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
GRIS = (128, 128, 128)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
NARANJA = (255, 165, 0)
PURPURA = (128, 0, 128)
AZUL = (0, 0, 255)

# Configuración de la fuente
pygame.font.init()
fuente = pygame.font.Font(None, 20)

class Nodo:
    def __init__(self, fila, col, ancho, total_filas):
        self.fila = fila
        self.col = col
        self.x = fila * ancho
        self.y = col * ancho
        self.color = BLANCO
        self.ancho = ancho
        self.total_filas = total_filas
        self.g = float("inf")  # Costo desde el inicio
        self.h = 0  # Distancia heurística al final
        self.f = 0  # G + H
        self.padre = None  # Nodo padre para reconstruir el camino

    def __lt__(self, other):
        return self.f < other.f

    def get_pos(self):
        return self.fila, self.col

    def es_pared(self):
        return self.color == NEGRO

    def es_inicio(self):
        return self.color == NARANJA

    def es_fin(self):
        return self.color == PURPURA

    def restablecer(self):
        self.color = BLANCO
        self.g = float("inf")
        self.h = 0
        self.f = 0
        self.padre = None

    def hacer_inicio(self):
        self.color = NARANJA

    def hacer_pared(self):
        self.color = NEGRO

    def hacer_fin(self):
        self.color = PURPURA

    def dibujar(self, ventana):
        pygame.draw.rect(ventana, self.color, (self.x, self.y, self.ancho, self.ancho))

        texto_g = fuente.render(f"G: {self.g}", True, NEGRO)
        texto_h = fuente.render(f"H: {self.h}", True, NEGRO)
        texto_f = fuente.render(f"F: {self.f}", True, NEGRO)

        ventana.blit(texto_g, (self.x + 2, self.y + 2))
        ventana.blit(texto_h, (self.x + 2, self.y + 18))
        ventana.blit(texto_f, (self.x + 2, self.y + 34))

def crear_grid(filas, ancho):
    grid = []
    ancho_nodo = ancho // filas
    for i in range(filas):
        grid.append([])
        for j in range(filas):
            nodo = Nodo(i, j, ancho_nodo, filas)
            grid[i].append(nodo)
    return grid

def dibujar_grid(ventana, filas, ancho):
    ancho_nodo = ancho // filas
    for i in range(filas):
        pygame.draw.line(ventana, GRIS, (0, i * ancho_nodo), (ancho, i * ancho_nodo))
        for j in range(filas):
            pygame.draw.line(ventana, GRIS, (j * ancho_nodo, 0), (j * ancho_nodo, ancho))

def dibujar(ventana, grid, filas, ancho):
    ventana.fill(BLANCO)
    for fila in grid:
        for nodo in fila:
            nodo.dibujar(ventana)

    dibujar_grid(ventana, filas, ancho)
    pygame.display.update()

def obtener_click_pos(pos, filas, ancho):
    ancho_nodo = ancho // filas
    y, x = pos
    fila = y // ancho_nodo
    col = x // ancho_nodo
    return fila, col

def calcular_heuristica(nodo, fin):
    return (abs(nodo.fila - fin.fila) + abs(nodo.col - fin.col)) * 10

def vecinos(nodo, grid, filas):
    vecinos = []
    direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)] #arriba,abajo,izq,der
    for d in direcciones:
        fila = nodo.fila + d[0]
        col = nodo.col + d[1]
        if 0 <= fila < filas and 0 <= col < filas:
            vecinos.append(grid[fila][col])
    return vecinos

def a_star(grid, inicio, fin, filas):
    open_list = []
    closed_list = []

    inicio.g = 0
    inicio.h = calcular_heuristica(inicio, fin)
    inicio.f = inicio.g + inicio.h

    heapq.heappush(open_list, inicio)

    while open_list:
        nodo_actual = heapq.heappop(open_list)
        closed_list.append(nodo_actual)

        if nodo_actual != inicio and nodo_actual != fin:
            nodo_actual.color = GRIS

        if nodo_actual == fin:
            path = []
            current = nodo_actual
            while current.padre:
                path.append(current)
                current = current.padre
            path.append(inicio)

            for nodo in reversed(path):
                if nodo != inicio and nodo != fin:
                    nodo.color = VERDE
                dibujar(VENTANA, grid, filas, ANCHO_VENTANA)
                pygame.time.delay(300)
            return

        for vecino in vecinos(nodo_actual, grid, filas):
            if vecino in closed_list or vecino.es_pared():
                continue

            temp_g = nodo_actual.g + (10 if abs(nodo_actual.fila - vecino.fila) + abs(nodo_actual.col - vecino.col) == 1 else 14)

            if vecino not in open_list:
                vecino.g = temp_g
                vecino.h = calcular_heuristica(vecino, fin)
                vecino.f = vecino.g + vecino.h
                vecino.padre = nodo_actual
                heapq.heappush(open_list, vecino)
            else:
                if temp_g < vecino.g:
                    vecino.g = temp_g
                    vecino.f = vecino.g + vecino.h
                    vecino.padre = nodo_actual

        dibujar(VENTANA, grid, filas, ANCHO_VENTANA)
        pygame.time.delay(100)

def main(ventana, ancho):
    FILAS = 11  # tamaño
    grid = crear_grid(FILAS, ancho)
    
    inicio = None
    fin = None

    corriendo = True

    while corriendo:
        dibujar(ventana, grid, FILAS, ancho)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                corriendo = False

            if pygame.mouse.get_pressed()[0]:  #para seleccionar
                pos = pygame.mouse.get_pos()
                fila, col = obtener_click_pos(pos, FILAS, ancho)
                nodo = grid[fila][col]
                if not inicio and nodo != fin:
                    inicio = nodo
                    inicio.hacer_inicio()

                elif not fin and nodo != inicio:
                    fin = nodo
                    fin.hacer_fin()

                elif nodo != fin and nodo != inicio:
                    nodo.hacer_pared()

            elif pygame.mouse.get_pressed()[2]: #para borrar
                pos = pygame.mouse.get_pos()
                fila, col = obtener_click_pos(pos, FILAS, ancho)
                nodo = grid[fila][col]
                nodo.restablecer()
                if nodo == inicio:
                    inicio = None
                elif nodo == fin:
                    fin = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:  #"e" para iniciar
                    if inicio and fin:
                        try:
                            a_star(grid, inicio, fin, FILAS)
                        except Exception as e:
                            print(f"Error al ejecutar A*: {e}")
                            continue

    pygame.quit()

main(VENTANA, ANCHO_VENTANA)