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
   for z in range(len(tablero)) :
       for x in range(len(tablero)) :
           for y in range(len(tablero)) :
               if ' ' == tablero[z][x][y] :
                   return z,x,y    
   return None
