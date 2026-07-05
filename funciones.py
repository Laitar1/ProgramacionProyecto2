import json
import os
import random
from datetime import datetime

from colorama import Fore, Style, init

#inicializa colorama para que los colores funcionen en cualquier consola
init(autoreset=True)

#ruta del archivo donde se guardan las partidas jugadas
PARTIDAS_PATH = os.path.join(os.path.dirname(__file__), "partidas.json")

#variable global que guarda una copia del tablero al terminar cada partida
ULTIMO_TABLERO = None

#colores asignados a cada ficha para mostrarlas en consola
COLOR_PIEZAS = {
    "X": Fore.RED,  #fichas del jugador 1 en rojo
    "O": Fore.CYAN, #fichas del jugador 2 o computadora en cyan
    "_": Fore.WHITE,    #casilla vacía en blanco
}

#texto que se muestra para cada resultado al listar partidas
RESULTADOS_TEXTO = {
    "X": "X ganó",
    "O": "O ganó",
    "Empate": "Empate",
    "Cancelado": "Cancelado",
}




def guardar_partida(jugador1, jugador2, fecha, resultado):
    #guarda los datos de una partida terminada en partidas.json
    global ULTIMO_TABLERO
    partidas = cargar_partidas()    # carga las partidas previas
    partida = {
        "jugador1": jugador1,
        "jugador2": jugador2,
        "fecha": fecha,
        "resultado": resultado,
        "tablero": ULTIMO_TABLERO if ULTIMO_TABLERO is not None else [],    #guarda el tablero final
    }
    partidas.append(partida)             #agrega la nueva partida a la lista
    with open(PARTIDAS_PATH, "w", encoding="utf-8") as handle:
        json.dump(partidas, handle, indent=2)  #escribe todo el historial en el archivo


def registro():
    #muestra una tabla con todas las partidas jugadas y ver el tablero final de cada una
    partidas = cargar_partidas()
    if not partidas:
        print("No hay juegos realizados todavía.")
        return

    # Encabezado de la tabla
    print("\nJuegos realizados")
    print("Idx  Jugador 1                Jugador 2                Fecha y hora      Resultado")
    print("---  ------------------------  ------------------------  ----------------  ----------")

    #imprime cada partida en una fila de la tabla
    for idx, partida in enumerate(partidas, start=1):
        resultado = RESULTADOS_TEXTO.get(partida["resultado"], partida["resultado"])
        print(
            f"{idx:<3}  {partida['jugador1']:<24}  {partida['jugador2']:<24}  {partida['fecha']:<16}  {resultado}"
        )

    #permite al usuario elegir una partida para ver cómo quedó el tablero
    while True:
        seleccion = input("\nSeleccione un juego para ver el tablero final (0 para volver): ")
        if seleccion == "0":
            return
        if not seleccion.isdigit():
            print("Entrada inválida. Ingrese un número.")
            continue

        index = int(seleccion) - 1
        if 0 <= index < len(partidas):
            mostrar_tablero(partidas[index]["tablero"], titulo=f"Tablero final del juego {seleccion}")
            return
        print("Número de juego inválido.")


def cargar_partidas():
    #lee el archivo partidas.json y devuelve la lista de partidas. Si no existe o está dañado, devuelve lista vacía
    if not os.path.exists(PARTIDAS_PATH):
        return []
    try:
        with open(PARTIDAS_PATH, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (json.JSONDecodeError, OSError):
        return []


def crear_tablero():
    #crea y devuelve la matriz 8x8 con las fichas en su posición inicial
    tablero = []
    for fil in range(8):    #recorre las 8 filas
        filasT = []
        for colum in range(8):  #recorre las 8 columnas
            suma = fil + colum
            if fil in [0, 1]:
                #primeras dos filas: fichas del jugador O
                filasT.append("O" if suma % 2 == 1 else "_")
            elif fil in [6, 7]:
                #últimas dos filas: fichas del jugador X
                filasT.append("X" if suma % 2 == 1 else "_")
            else:
                #filas del centro: vacío
                filasT.append("_")
        tablero.append(filasT)
    return tablero


def colorizar_pieza(pieza):
    #devuelve el carácter de la pieza
    return COLOR_PIEZAS.get(pieza, Fore.WHITE) + pieza + Style.RESET_ALL


def mostrar_tablero(tablero, titulo=None):
   #imprime el tablero en consola con columnas A-H y filas 1-8, fichas coloreadas
    if titulo:
        print(f"\n{titulo}")
    print("  A B C D E F G H")
    for valor in range(8):
        linea = valor + 1
        print(linea, end=" ")
        for temporal in range(8):
            pieza = tablero[valor][temporal]
            print(colorizar_pieza(pieza), end=" ")
        print(linea)
    print("  A B C D E F G H")




def traductor(jugada):
    #convierte una jugada en texto (ej. 'A8C6') a coordenadas internas (fila, columna)
    #devuelve "Cancelado" si el usuario escribe -1, False si el formato es incorrecto, o una tupla de dos tuplas ((filaOrigen, colOrigen), (filaDestino, colDestino))
    if jugada == str(-1):
        return "Cancelado"
    if len(jugada) != 4:
        return False

    Columnas = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7}

    #extrae la letra y número de la casilla de origen
    letra_original = jugada[0].upper()
    if not jugada[1].isdigit():
        return False
    numero_original = int(jugada[1]) - 1    #convierte a índice 0-7

    #extrae la letra y número de la casilla de destino
    letra_final = jugada[2].upper()
    if not jugada[3].isdigit():
        return False
    numero_final = int(jugada[3]) - 1

    #valida que las letras y números estén dentro del tablero
    if letra_original not in Columnas or letra_final not in Columnas:
        return False
    if not (0 <= numero_original <= 7 and 0 <= numero_final <= 7):
        return False

    return (numero_original, Columnas[letra_original]), (numero_final, Columnas[letra_final])


def traductor_inverso(coordenadasbs):
    #convierte coordenadas internas a texto legible
    #se usa para mostrar el movimiento que eligió la computadora
    
    (filaOR, columnaOR), (filaFI, columnaFI) = coordenadasbs
    diccionarioOG = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7}
    diccionarioInvertido = {valor: clave for clave, valor in diccionarioOG.items()}
    return "".join(
        [diccionarioInvertido[columnaOR], str(filaOR + 1), diccionarioInvertido[columnaFI], str(filaFI + 1)]
    )



def verificador(tuplaoriginal, tuplafinal, tablero_actual, turno):
    #verifica si un movimiento es válido según las reglas del juego
    #revisa: ficha correcta, destino vacío, movimiento diagonal y distancia permitida
    
    posibles = [1, 2, 4, 6]   #distancias diagonales permitidas
    filaOR, columnaOR = tuplaoriginal
    filaFI, columnaFI = tuplafinal

    #la casilla de origen debe tener una ficha del jugador en turno
    if tablero_actual[filaOR][columnaOR] != turno:
        return False
    if tablero_actual[filaFI][columnaFI] != "_":
        return False

    distancia_fil = abs(filaFI - filaOR)
    distancia_col = abs(columnaFI - columnaOR)

    #el movimiento debe ser exactamente en diagonal
    if distancia_col != distancia_fil:
        return False
    #la distancia debe ser una de las permitidas
    if distancia_fil not in posibles:
        return False
    #dstancia 1 = movimiento simple
    if distancia_fil == 1:
        return True
    #distancia mayor = salto, se valida que haya fichas para saltar y casillas libres intermedias
    return validar_camino_salto(tablero_actual, tuplaoriginal, tuplafinal, distancia_fil)


def hay_ganador(tablero):
    #revisa si algún jugador ya ganó.
    #X gana si tiene 8 fichas en las filas 1-2
    #O gana si tiene 8 fichas en las filas 7-8
    #devuelve X, O o None si todavía no hay ganador

    ganador_x = 0
    ganador_o = 0

    for columna in range(8):
        if tablero[0][columna] == "X":
            ganador_x += 1
        if tablero[1][columna] == "X":
            ganador_x += 1
        if tablero[6][columna] == "O":
            ganador_o += 1
        if tablero[7][columna] == "O":
            ganador_o += 1

    if ganador_x == 8:
        return "X"
    if ganador_o == 8:
        return "O"
    return None   #todavía no hay ganador


def posibles_jugadas(tablero, ficha):
    #genera y devuelve todas las jugadas legales disponibles para una ficha dada
    #recorre todo el tablero buscando fichas del jugador y prueba cada dirección y distancia posible
    
    respuesta = []
    combinaciones = [1, 2, 4, 6]                          #distancias a probar
    direcciones = [(1, 1), (-1, 1), (1, -1), (-1, -1)]    #las 4 diagonales posibles

    for filas in range(8):
        for columnas in range(8):
            #solo analiza casillas que tengan fichas del jugador indicado
            if tablero[filas][columnas] != ficha:
                continue
            original = (filas, columnas)
            for dir_f, dir_c in direcciones:
                for variable in combinaciones:
                    filacp = filas + dir_f * variable
                    columnacp = columnas + dir_c * variable
                    #descarta si el destino está fuera del tablero
                    if not (0 <= filacp <= 7 and 0 <= columnacp <= 7):
                        continue
                    temporales = (filacp, columnacp)
                    if variable == 1:
                        #movimiento simple: solo necesita que el destino esté vacío
                        if tablero[filacp][columnacp] == "_":
                            respuesta.append((original, temporales))
                    else:
                        #salto: valida el camino y que el destino esté vacío
                        if validar_camino_salto(tablero, original, temporales, variable):
                            if tablero[filacp][columnacp] == "_":
                                respuesta.append((original, temporales))
    return respuesta


def validar_camino_salto(tablero, tuplaoriginal, tuplafinal, salto):
    #verifica que el camino para un salto sea válido:
    #en cada posición intermedia de aterrizaje debe haber una ficha 
    #las casillas de aterrizaje entre saltos deben estar vacías
    #devuelve True si el salto es legal, False si no

    filaOR, columnaOR = tuplaoriginal
    filaFI, columnaFI = tuplafinal

    #determina la dirección del movimiento (+1 o -1 por fila y columna)
    comparar = (filaFI - filaOR) // abs(filaFI - filaOR)
    comparar2 = (columnaFI - columnaOR) // abs(columnaFI - columnaOR)
    direcciones = [(1, 1), (-1, 1), (1, -1), (-1, -1)]

    #identifica qué dirección diagonal corresponde
    for simbolo_fil, simbolo_col in direcciones:
        if simbolo_fil == comparar and simbolo_col == comparar2:
            break

    #comprueba que en cada posición de "ficha a saltar" haya una pieza
    chequeo = salto // 2
    calc_temp_fil = filaOR + simbolo_fil
    calc_temp_col = columnaOR + simbolo_col
    while chequeo > 0:
        if tablero[calc_temp_fil][calc_temp_col] == "_":
            return False   # no hay ficha para saltar
        calc_temp_fil += 2 * simbolo_fil
        calc_temp_col += 2 * simbolo_col
        chequeo -= 1

    #comprueba que las casillas intermedias de aterrizaje estén vacías
    chequeo = salto // 2
    calc_temp_fil = filaOR + 2 * simbolo_fil
    calc_temp_col = columnaOR + 2 * simbolo_col
    while chequeo > 1:
        if tablero[calc_temp_fil][calc_temp_col] != "_":
            return False   #hay una ficha bloqueando el aterrizaje intermedio
        calc_temp_fil += 2 * simbolo_fil
        calc_temp_col += 2 * simbolo_col
        chequeo -= 1
    return True



def elegir_jugada_computadora(tablero, ficha):
    #elige la jugada que realizará la computadora
    #descarta fichas que ya llegaron a la meta
    #prioriza saltos largos hacia adelante
    #si no hay saltos largos, elige cualquier jugada válida al azar

    jugadas = posibles_jugadas(tablero, ficha)   #lista de todas las jugadas legales

    #descarta fichas que ya cruzaron al lado contrario
    meta = [6, 7]
    pendientes = []
    for valor in jugadas:
        (Fil_or, _), _ = valor
        if Fil_or not in meta:
            pendientes.append(valor)
    if pendientes:
        jugadas = pendientes   #si hay fichas sin llegar, solo considera esas

    #busca saltos largos hacia adelante para avanzar más rápido
    multiples = []
    for valor in jugadas:
        (Fil_or, _), (Fil_fi, _) = valor
        distancia_fil = abs(Fil_fi - Fil_or)
        if distancia_fil in [4, 6] and Fil_fi > Fil_or:
            multiples.append(valor)

    if multiples:
        return random.choice(multiples)   #elige un salto largo al azar
    return random.choice(jugadas)          #si no hay, elige cualquier jugada válida al azar




def pedir_nombre_jugador():
    #pide y valida los nombres de los dos jugadores antes de empezar la partida
    #no permite nombres vacíos ni nombres iguales
    
    while True:
        Jugador_1 = input("Nombre jugador 1 : ")
        Jugador_2 = input("Nombre jugador 2 : ")

        #validaciones de nombres
        if Jugador_1.strip() == "" and Jugador_2.strip() == "":
            print("Error, nombres no pueden estar vacios")
            continue
        if Jugador_1 == Jugador_2:
            print("No se aceptan nombres iguales, disculpe las molestias")
            continue
        if Jugador_1.strip() == "":
            print('Error, nombre vacio en "Jugador 1"')
            continue
        if Jugador_2.strip() == "":
            print('Error, nombre vacio en "Jugador 2"')
            continue

        #pide confirmación de los nombres antes de continuar
        while True:
            flag = input("Confirmar nombres (S/N): ").strip().upper()
            if flag == "S":
                return Jugador_1, Jugador_2
            if flag == "N":
                break
            print("Opción inválida")


def jugador_turno():
    #pide el nombre del jugador en el modo vs computadora y si quiere jugar primero o segundo
    #no permite nombres vacíos ni usar 'computador' como nombre
    #devuelve (nombre_jugador, S o N) donde cuando elijes S el jugador va primero
    
    while True:
        Jugador = input("Nombre del jugador : ")
        if Jugador.strip() == "":
            print("Error, nombre no puede estar vacios")
            continue
        if Jugador.lower() == "computador":
            print("Error, nombre inviable. Hagame el favor de cambiarlo")
            continue

        #confirma el nombre
        while True:
            flag = input("Confirmar nombre (S/N): ").strip().upper()
            if flag == "S":
                #pregunta si el jugador quiere ir primero
                while True:
                    turno = input("Juega primero? (S/N): ").strip().upper()
                    if turno in ["S", "N"]:
                        return Jugador, turno
                    print("Opción inválida")
            elif flag == "N":
                break   #vuelve a pedir el nombre
            else:
                print("Opción inválida")




def turno_local(tablero):
    #maneja el ciclo completo de una partida entre dos jugadores humanos
    #alterna turnos, valida movimientos, detecta ganador/empate/cancelación y guarda la partida al terminar

    global ULTIMO_TABLERO
    print("Jugador 1, comienza la partida")
    Jugador_1, Jugador_2 = pedir_nombre_jugador()

    #aigna las fichas a cada jugador
    fichas = {Jugador_1: "X", Jugador_2: "O"}
    Jugador = Jugador_1         #el jugador 1 siempre empieza
    turno_actual = fichas[Jugador]

    fecha = datetime.now().strftime("%d/%m/%y %H:%M")
    print(f"Juego {Jugador_1} vs {Jugador_2} {fecha}")
    print("−1: Cancelar juego")

    while True:
        #comprueba si algún jugador ya ganó antes de mostrar el tablero
        if hay_ganador(tablero) == "X":
            print(f"Ganador: {Jugador_1}")
            ULTIMO_TABLERO = [fila.copy() for fila in tablero]
            guardar_partida(Jugador_1, Jugador_2, fecha, Jugador_1)
            break
        if hay_ganador(tablero) == "O":
            print(f"Ganador: {Jugador_2}")
            ULTIMO_TABLERO = [fila.copy() for fila in tablero]
            guardar_partida(Jugador_1, Jugador_2, fecha, Jugador_2)
            break

        mostrar_tablero(tablero)

        #si el jugador en turno no tiene movimientos, termina en empate (rey ahogado)
        if not posibles_jugadas(tablero, turno_actual):
            print("partida terminada por rey ahogado")
            ULTIMO_TABLERO = [fila.copy() for fila in tablero]
            guardar_partida(Jugador_1, Jugador_2, fecha, "Empate")
            break

        #pide el movimiento al jugador en turno
        movimiento_realizado = input(f"{Jugador} Movimiento(formato A8C6): ")
        coordenadas = traductor(movimiento_realizado)

        if coordenadas == "Cancelado":
            print("Juego cancelado")
            ULTIMO_TABLERO = [fila.copy() for fila in tablero]
            guardar_partida(Jugador_1, Jugador_2, fecha, "Cancelado")
            break
        if coordenadas is False:
            print("Jugada inválida, formato A8C6")
            continue   #vuelve a pedir el movimiento sin cambiar de turno

        tuplaoriginal, tuplafinal = coordenadas

        if verificador(tuplaoriginal, tuplafinal, tablero, turno_actual):
            #movimiento válido: actualiza el tablero y cambia de turno
            filaOR, columnaOR = tuplaoriginal
            filaFI, columnaFI = tuplafinal
            tablero[filaFI][columnaFI] = turno_actual
            tablero[filaOR][columnaOR] = "_"
            Jugador = Jugador_2 if Jugador == Jugador_1 else Jugador_1
            turno_actual = fichas[Jugador]
        else:
            print("Movimiento inválido.")   #el movimiento no cumple las reglas


def turno_computadora(tablero):
    #maneja el ciclo completo de una partida jugador vs computadora
    #cuando le toca a la computadora, elige su jugada con elegir_jugada_computadora
    #cuando le toca al jugador, pide el movimiento por teclado
    #al terminar guarda la partida
    
    global ULTIMO_TABLERO
    print("El futuro está en tus manos")
    Jugador, turno = jugador_turno()

    #asigna fichas: el jugador siempre usa X, la computadora usa O
    fichas = {Jugador: "X", "Computador": "O"}
    Partida = Jugador if turno == "S" else "Computador"   #define quién empieza
    turno_actual = fichas[Partida]

    fecha = datetime.now().strftime("%d/%m/%y %H:%M")
    print(f"Juego {Jugador} vs Computador (Alias Mechanus Calsen) {fecha}")
    print("−1: Cancelar juego")

    while True:
        #comprueba si alguien ganó antes de mostrar el tablero
        if hay_ganador(tablero) == "X":
            print(f"Ganador: {Jugador}")
            ULTIMO_TABLERO = [fila.copy() for fila in tablero]
            guardar_partida(Jugador, "Computador", fecha, Jugador)
            break
        if hay_ganador(tablero) == "O":
            print("Ganador: Computador")
            ULTIMO_TABLERO = [fila.copy() for fila in tablero]
            guardar_partida(Jugador, "Computador", fecha, "Computador")
            break

        mostrar_tablero(tablero)

        #si quien tiene el turno no puede moverse, termina en empate
        if not posibles_jugadas(tablero, turno_actual):
            print("partida terminada por rey ahogado")
            ULTIMO_TABLERO = [fila.copy() for fila in tablero]
            guardar_partida(Jugador, "Computador", fecha, "Empate")
            break

        if Partida == "Computador":
            #le toca a la computadora: elige su jugada automáticamente
            coordenadas = elegir_jugada_computadora(tablero, turno_actual)
            redaccion = traductor_inverso(coordenadas)
            print(f"{Partida} ? {redaccion}")
        else:
            #le toca al jugador: pide el movimiento por teclado
            movimiento_realizado = input(f"{Partida} ?(formato A8C6): ")
            coordenadas = traductor(movimiento_realizado)

        if coordenadas == "Cancelado":
            print("Juego cancelado")
            ULTIMO_TABLERO = [fila.copy() for fila in tablero]
            guardar_partida(Jugador, "Computador", fecha, "Cancelado")
            break
        if coordenadas is False:
            print("Jugada inválida, formato A8C6")
            continue   #vuelve a pedir sin cambiar de turno

        tuplaoriginal, tuplafinal = coordenadas

        if verificador(tuplaoriginal, tuplafinal, tablero, turno_actual):
            #movimiento válido: actualiza tablero y alterna el turno
            filaOR, columnaOR = tuplaoriginal
            filaFI, columnaFI = tuplafinal
            tablero[filaFI][columnaFI] = turno_actual
            tablero[filaOR][columnaOR] = "_"
            Partida = "Computador" if Partida == Jugador else Jugador
            turno_actual = fichas[Partida]
        else:
            print("Movimiento inválido.")