#       
# Universidad Nacional de Itapua
# Inteligencia Artificial
# 7mo Semestre
#
# Proyecto#2: Torneo Ta-te-ti 3d
# Alumna: Tania Priscila Schulz Villalba

from collections import defaultdict
import time 

PROFUNDIDAD_MAXIMA = 5 # profundidad maxima para busqueda iterativa
# limites de tiempo para evitar timeouts
INICIO_GLOBAL = None 
LIMITE_GLOBAL = None
# nodos para verificar timeout, para no verificar constantemente
NODOS_CONTADOS = 0 
NODOS_PARA_REVISAR = 50

# lista de 13 direcciones (dz, dx, dy)
# usamos solo 13 para disminuir duplicados (lineas iguales pero en sentido contrario)
# regla para evitar duplicados: solo direcciones donde el primer componente no nulo sea positivo. 
DIRECCIONES = ( 
    # con dz positivo
    (1, 0, 0),
    (1, 1, 0),
    (1, 0, 1),
    (1, 1, 1),
    (1, -1, 0),
    (1, 0, -1),
    (1, -1, -1),
    (1, -1, 1),
    (1, 1, -1),
    # con dx positivo (ignorando dz = -1)
    (0, 1, 0),
    (0, 1, 1),
    (0, 1, -1),
    # con dy positivo (ignorando dz = -1, dx = -1)
    (0, 0, 1),
)

# generar las 76 lineas posibles del juego
# toma cada una da las casillas y genera lineas en las 13 direcciones, 
# ignorando duplicados
def generar_lineas() :
    # set de lineas - ignora duplicadas
    lineas = set()
    # indices de que lineas forma parte una coordenada
    # para faciliar la deteccion de fin de juego
    indice = defaultdict(list)
    # recorrer cada casilla del tablero
    for z in range(4):
       for x in range(4):
           for y in range(4):
               casilla = (z, x, y)
               # probar con cada direccion
               for dir in DIRECCIONES: 
                # contiene las 4 coordenadas de la linea nueva
                linea = []
                # tomar 4 pasos en la direccion actual
                for paso in range(4):
                    nueva_z = casilla[0] + paso * dir[0]
                    # verificar si la coordenada es valida (entre 0 y 3)
                    # si no es valida, finalizamos (la linea es invalida)
                    if nueva_z < 0 or nueva_z > 3 : break

                    nueva_x = casilla[1] + paso * dir[1]
                    # verificar si la coordenada es valida 
                    if nueva_x < 0 or nueva_x > 3 : break

                    nueva_y = casilla[2] + paso * dir[2]
                    # verificar si la coordenada es valida
                    if nueva_y < 0 or nueva_y > 3 : break

                    linea.append((nueva_z, nueva_x, nueva_y))

                # verificar que la linea no tenga invalidas (menos de 4 coord)
                # si es invalida no usamos la linea
                if len(linea) < 4: continue

                # ordenar las coordenadas y agregar al set
                # se convierte a tupla pq debe ser hashable para set
                linea_tupla = tuple(sorted(linea))
                lineas.add(linea_tupla)

                for coord in linea_tupla:
                    indice[coord].append(linea_tupla)

    return lineas, indice

# generar las lineas e indices
LINEAS, INDICE = generar_lineas()

# obtiene que hay en el tablero en una coordenada dada (z, x, y)
def get_coordenada(tablero, coordenada): 
    return tablero[coordenada[0]][coordenada[1]][coordenada[2]]

# devuelve el simbolo del oponente
def get_oponente(simbolo):
    if simbolo == 'X' : return 'O'
    elif simbolo == 'O' : return 'X'
    else : return None

# devuelve la primera coordenada vacia del tablero, o None si no hay
# utilizada como respaldo si minimax falla
def primera_vacia(tablero):
    for z in range(4):
        for x in range(4):
            for y in range(4):
                if tablero[z][x][y] == ' ':
                    return (z, x, y)
    return None

# utilizado para saber si somos X o O
# necesario para calcular la heuristica correctamente
# si contador_X == contador_O, soy X (porque X empieza siempre)
# Si contador_X == contador_O + 1, soy O
def get_simbolo(tablero) :
    contador_X = 0
    contador_O = 0 

    # contar cada simbolo del tablero           
    for z in range(4):
        for x in range(4):
            for y in range(4):
                if tablero[z][x][y] == 'X' : contador_X += 1
                elif tablero[z][x][y] == 'O' : contador_O += 1

    # comparar y elegir el simbolo 
    if contador_X == contador_O : return 'X'
    elif contador_X == (contador_O + 1) : return 'O'
    else : return None

# contar cantidad de simbolos mios, del oponente, Vacios en una linea dada
def get_conteo_linea(tablero, linea, simbolo, oponente):
    mio = 0
    op = 0
    vacio = 0
    for c in linea:
        elemento = get_coordenada(tablero, c)
        if elemento == simbolo : mio += 1
        elif elemento == oponente : op += 1
        elif elemento == ' ' : vacio += 1
    return (mio, op, vacio)

# CRITERIO DE ORDENAMIENTO: por cada LINEA donde aparece la celda:
# - si hay 3 de mi simbolo y 1 vacio: 5000 p (gano)
# - si hay 2 de mi simbolo y 2 vacios: 100 p 
# - si hay 1 de mi simbolo y 3 vacios: 10 p
# - si hay 3 del oponente y 1 vacio: 1000 p (bloquearle)
# - si hay 2 del oponente y 2 vacios: 100 p 
# - si hay 1 del oponente y 3 vacios: 10 puntos
def puntaje_linea(mio, op, vacio):
    if op == 0:
        if mio == 3 and vacio == 1 : return 5000
        if mio == 2 and vacio == 2 : return 100
        if mio == 1 and vacio == 3 : return 10
    if mio == 0:
        if op == 3 and vacio == 1 : return 1000
        if op == 2 and vacio == 2 : return 100
        if op == 1 and vacio == 3 : return 10
    return 0

# genera los posibles sucesores 
# se le aplica un criterio de ordenamiento para optimizar alfa-beta
# asi se revisan los casos mas relevantes primero y no se pierde tanto tiempo 
def generar_sucesores(tablero, simbolo, oponente) : 
    sucesores = []
    # recorrer tablero buscando celdas vacios         
    for z in range(4):
        for x in range(4):
            for y in range(4):
                if tablero[z][x][y] == ' ' :
                    coord = (z, x, y)
                    puntaje = 0
                    # sucesores.append((z, x, y))

                    # obtener lineas en las que aparece la coordenada
                    lineas = INDICE[coord]
                    for l in lineas : 
                        # asignar puntaje a la linea y sumar al total 
                        conteo = get_conteo_linea(tablero, l, simbolo, oponente)
                        puntaje += puntaje_linea(conteo[0], conteo[1], conteo[2])

                    # crear el sucesor 
                    sucesores.append((puntaje, coord)) 

    # ordenar por puntaje mas alto y retornar coordenadas sucesoras 
    sorted_sucesores = sorted(sucesores, key=lambda x: x[0], reverse=True)
    return [coord for puntaje, coord in sorted_sucesores]
        
# obtener la heuristica de la jugada
def evaluar_heuristica(tablero, simbolo, oponente) : 
    puntaje = 0
    #hay_vacias = False # para detectar empate (tablero lleno)

    # Amenazas multiples: cuando se puede ganar en varias lineas a la vez, 
    # se suman los puntajes de cada linea
    amenazas_mias = 0
    amenazas_oponente = 0

    for l in LINEAS : 
        # obtener conteo de lineas
        mio, op, vacio = get_conteo_linea(tablero, l, simbolo, oponente)
        
        #if vacio > 0 : hay_vacias = True 
        #if mio == 4 : return 100000000 # victoria
        #if op == 4 : return -100000000 # derrota

        # heuristica
        if op == 0: 
            if mio == 3 and vacio == 1 : 
                puntaje += 1000
                amenazas_mias += 1
            if mio == 2 and vacio == 2 : puntaje += 100
            if mio == 1 and vacio == 3 : puntaje += 10
        if mio == 0:
            if op == 3 and vacio == 1 : 
                puntaje += -1000
                amenazas_oponente += 1
            if op == 2 and vacio == 2 : puntaje += -100
            if op == 1 and vacio == 3 : puntaje += -10

    # premiar o castigar mucho las multiples amenazas
    if amenazas_mias >= 2 : puntaje += 10000
    if amenazas_oponente >= 2 : puntaje += -10000

    return puntaje

def fin_del_juego(tablero, coordenada, simbolo, profundidad) : 
    #  utilizada para dar mas / menos peso segun profundidad
    # para que minimax prefiera soluciones de menor profundidad
    K = 1000 
    oponente = get_oponente(simbolo)

    # verificar si se llenaron 4 espacios en las lineas de la coordenada
    lineas = INDICE[coordenada]
    for l in lineas : 
        mio, op, vacio = get_conteo_linea(tablero, l, simbolo, oponente)
        if mio == 4 : return 100000000 + profundidad * K # victoria
        if op == 4 : return -100000000 - profundidad * K # derrota

    # si no es el fin todavia
    return None

# minimax recursivo con poda alfa beta
def minimax(tablero, coordenada, profundidad, mi_simbolo, simbolo_actual, alfa, beta):
    global NODOS_CONTADOS
    NODOS_CONTADOS += 1
    if NODOS_CONTADOS >= NODOS_PARA_REVISAR:
        NODOS_CONTADOS = 0
        if time.perf_counter() - INICIO_GLOBAL > LIMITE_GLOBAL:
            raise TimeoutError("Tiempo agotado")
    
    oponente = get_oponente(simbolo_actual)
    mi_oponente = get_oponente(mi_simbolo)
    # casos base: fin del juego o profundidad 0
    fin = fin_del_juego(tablero, coordenada, mi_simbolo, profundidad) 
    if fin != None : return fin

    if profundidad == 0 : 
        return evaluar_heuristica(tablero, mi_simbolo, mi_oponente)

    # generar posibles sucesores 
    sucesores = generar_sucesores(tablero, simbolo_actual, oponente)
    if sucesores == [] : return 0 # empate
    
    # mi turno: caso maximizacion
    if mi_simbolo == simbolo_actual :
        v = float("-inf")

        for s in sucesores : 
            tablero[s[0]][s[1]][s[2]] = mi_simbolo
            valor = minimax(tablero, s, profundidad-1, mi_simbolo, oponente, alfa, beta)
            tablero[s[0]][s[1]][s[2]] = ' ' # deshacer la jugada
            v = max(v, valor)
            alfa = max(v, alfa)
            if alfa >= beta : break # poda
        return v

    # turno del oponente: caso minimizacion
    if mi_simbolo != simbolo_actual :
        v = float("inf")
    
        for s in sucesores : 
            tablero[s[0]][s[1]][s[2]] = simbolo_actual
            valor = minimax(tablero, s, profundidad-1, mi_simbolo, oponente, alfa, beta)
            tablero[s[0]][s[1]][s[2]] = ' ' # deshacer la jugada
            v = min(v, valor)
            beta = min(v, beta)
            if beta <= alfa : break # poda
        return v   
 
    else : return None 

# buscar la mejor jugada en la raiz 
def buscar_mejor_jugada(tablero, profundidad):
    simbolo = get_simbolo(tablero)
    oponente = get_oponente(simbolo)

    mejor_jugada = None
    mejor_valor = float("-inf")

    # generar sucesores y ordenarlos por heuristica
    sucesores = generar_sucesores(tablero, simbolo, oponente)

    for s in sucesores:
        if time.perf_counter() - INICIO_GLOBAL > LIMITE_GLOBAL:
            raise TimeoutError("Tiempo límite alcanzado durante la búsqueda de la mejor jugada.")

        tablero[s[0]][s[1]][s[2]] = simbolo
        v = minimax(tablero, s, profundidad - 1, simbolo, oponente, mejor_valor, float("inf"))
        tablero[s[0]][s[1]][s[2]] = ' '  # deshacer la jugada

        if v > mejor_valor:
            mejor_valor = v
            mejor_jugada = s

    return mejor_jugada, mejor_valor
                
def jugar(tablero, tiempo) :
    global INICIO_GLOBAL, LIMITE_GLOBAL, NODOS_CONTADOS
    INICIO_GLOBAL = time.perf_counter() # tiempo en segundos
    LIMITE_GLOBAL = tiempo / 1000 * 0.75
    NODOS_CONTADOS = 0 # reinicializar contador de nodos

    mejor_jugada = primera_vacia(tablero)  # respaldo si minimax falla

    # profundidad iterativa
    for profundidad in range(1, PROFUNDIDAD_MAXIMA + 1):
        if time.perf_counter() - INICIO_GLOBAL > LIMITE_GLOBAL:
            break
        
        try:
            jugada, valor = buscar_mejor_jugada(tablero, profundidad)
            if jugada is not None : mejor_jugada = jugada
        except TimeoutError:
            break  # descartar esta profundidad
    
    return mejor_jugada

