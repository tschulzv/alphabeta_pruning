# 
# Universidad Nacional de Itapua
# Inteligencia Artificial
# 7mo Semestre
#
# Proyecto#2: Torneo Ta-te-ti 3d
#
# Autor: Amin Mansuri modificado por Wildo Monges
#
# NO ES NECESARIO MODIFICAR ESTE ARCHIVO
#


import random

def jugar(tablero, tiempo) :
   while True :
       z = random.randint(0,len(tablero)-1)
       x = random.randint(0,len(tablero[z])-1)
       y = random.randint(0,len(tablero[z][x])-1)
       if ' ' == tablero[z][x][y] :
           return z,x,y    
