from funciones import crear_tablero, registro, turno_computadora, turno_local


def main():
    #bucle principal: se repite hasta que el usuario elige salir
    while True:
        #muestra las opciones del menú
        print("\nJUEGO DAMAS CHINAS")
        print("1. Comenzar Juego")
        print("2. Jugar vs Computadora")
        print("3. Juegos realizados")
        print("0. Salir")

        opcion = input("Opcion: ")

        if opcion == "1":
            #modo dos jugadores: crea el tablero y lanza la partida local
            tablero = crear_tablero()
            turno_local(tablero)

        elif opcion == "2":
            #modo contra la computadora: crea el tablero y lanza ese modo
            tablero = crear_tablero()
            turno_computadora(tablero)

        elif opcion == "3":
            #muestra el historial de partidas guardadas en partidas.json
            registro()

        elif opcion == "0":
            #el usuario elige salir, se rompe el bucle
            break

        else:
            #control de errores: si el usuario escribe algo que no es 0-3 se vuelve a pedir
            print("Opcion invalida, vuelva a intentarlo")

    print("Esperamos se haya divertido")


#punto de entrada: solo se ejecuta si se corre este archivo directamente
if __name__ == "__main__":
    main()