#
# Universidad Nacional de Itapua
# Inteligencia Artificial - 7mo Semestre
#
# Proyecto#2: Torneo de Ta-Te-Ti 3D
#
# Autor: Amin Mansuri modificado por wildo monges
#
#
# MODIFICACIONES REALIZADAS: cambio tiempo_millis(), que ahora
# devuelve milisegundos reales (el original devuelve el campo de microsegundos
# del segundo actual). 
#

# modulo para cargar archivos
import glob

# tiempo
import time


# Imprime el tablero de forma mas bonita
#
def imprimir(ttt3d) :
    print('Tablero')
    for nivel in ttt3d :
       for fila in nivel :
           print(fila)
       print('')

# Determina cual de los jugadores gano
#
def ganador(ttt3d, jugadores) :
    # para identificar el primer bit
    mascara = 1

    # usar 8 posibles direcciones
    # direccion es un numero binario de la forma
    # 001 a 111 donde cada bit indica si incrementar
    # en Z,X, o Y respectivamente 
    for direccion in range(1,8) :
     for jugador in range(len(jugadores)) :   
       # para cada posible posicion incial
       for z in range(len(ttt3d)) :
           for x in range(len(ttt3d[z])) :
               for y in range(len(ttt3d[z][x])) :
                   gano = False
                   #print '.'
                   # dar cuatro pasos en la direccion actual
                   for i in range(len(ttt3d[z][x])) :
                       gano = False
                       pz = z + i*(direccion&mascara)
                       px = x + i*((direccion>>1)&mascara)
                       py = y + i*((direccion>>2)&mascara)
                       if pz >= len(ttt3d) :
                           continue
                       if px >= len(ttt3d[pz]) :
                           continue
                       if py >= len(ttt3d[pz][px]) :
                           continue          
                       #print(pz,px,py
                       if jugadores[jugador] != ttt3d[pz][px][py] :
                           break
                       gano = True
                   if gano :
                       return jugador                 
    return None

# Calcula el tiempo
#
def tiempo_millis() :
    return time.perf_counter() * 1000


# Juega un partido entre dos jugadores
#
def jugar(jugador1,jugador2, nombre1, nombre2) :

    print('Bienvenidos a la competencia de Ta Te Ti 3D!')
    print('Los competidores de hoy son:',nombre1,'vs',nombre2)

    # crear tablero
    tablero = [[[' ',' ',' ',' '],
               [' ',' ',' ',' '],
               [' ',' ',' ',' '],
               [' ',' ',' ',' ']] for i in range(4)]




    simbolo = ('X','O')
    jugadores = (jugador1, jugador2)
    nombres = (nombre1, nombre2)
    n = 0

    # no hay ganador todavia
    g = None

    # mientras no hay ganador
    while None == g :
        # copiar preventivamente el tablero (evitar trampa)
        copia_tablero = [[row[:] for row in nivel] for nivel in tablero]
        inicio = tiempo_millis()
        j = jugadores[n%2](copia_tablero, tiempo)
        fin = tiempo_millis()
        t = fin - inicio
        print(nombres[n%2],'juega',j,'en',t,'ms')
        z,x,y = j
        if ' ' != tablero[z][x][y] :
            print('Jugada ilegal, jugador',nombres[(n%2)],'descalificado')
            g = (n+1)%2
            break
        if t > tiempo :
            print('Jugada ilegal, jugador',nombres[(n%2)],'descalificado')
            g = (n+1)%2
            break
        # coloca la ficha en el tablero
        tablero[z][x][y]=simbolo[n%2]
        n+=1
        g = ganador(tablero,simbolo)

    if None != g :
       print('El ganador es ',nombres[g],' en ',n,'jugadas')

    imprimir(tablero)
    return g

#========================
# INICIO TORNEO
# Esto busca archivos nombrados jugador_*.py y los juega
# Nota: supone que hay numero par de jugadores
#========================

tiempo = 500 # milisegundos


# cargar jugadores
# lista fija en lugar de glob, para elegir quienes juegan.
# El primero de la lista juega con X (empieza). Usar cantidad par.
archivos = ['jugador_aleatorio.py', 'jugador_tania.py', 'jugador_aleatorio2.py', 'jugador_libre.py']
#archivos = glob.glob('jugador_*.py')
jugadores = []
nombres = []
for a in archivos :
   try : 
       # sacar .py
       a = a[:-3]
       mod = __import__(a)
       jugadores.append(mod.jugar)
       nombres.append(a)
   except ImportError as e :
       print('Error loading', a, 'ignored', e)

ronda = jugadores[:]
nronda = nombres[:]
while len(ronda) > 1 :
  # jugar en pares
  i = 0
  nueva_ronda = []
  nueva_nronda = []
  print('datos',ronda, nronda)
  while i < len(ronda)-1 :
     g = jugar(ronda[i],ronda[i+1],nronda[i],nronda[i+1])
     nueva_ronda.append(ronda[i+g])
     nueva_nronda.append(nronda[i+g])
     i+=2
     
  ronda = nueva_ronda
  nronda = nueva_nronda

print('RESULTADOS FINALES')
print('El ganador es', nronda[0])