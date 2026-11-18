from taxi import Taxi

# Creamos nuestro objeto Taxi
taxi = Taxi()

# Mostramos el título de la aplicación
print("=============================")
print("          TAXITECH")
print("      TAXÍMETRO DIGITAL")
print("=============================")

# Mantenemos el programa funcionando
while True:

    # Mostramos las opciones del menú
    print("\n--------- MENÚ ---------")
    print("1. Iniciar carrera")
    print("2. Taxi en movimiento")
    print("3. Taxi parado")
    print("4. Consultar importe")
    print("5. Salir")
    print("------------------------")

    # Leemos la opción introducida
    opcion = input("Selecciona una opción: ")

    # US-01: Iniciar carrera
    if opcion == "1":
        taxi.iniciar_carrera()

    # US-02: Cambiar a movimiento
    elif opcion == "2":
        taxi.iniciar_movimiento()

    # US-02: Cambiar a parado
    elif opcion == "3":
        taxi.detener_movimiento()

    # US-02: Consultar cuánto debemos cobrar
    elif opcion == "4":
        taxi.consultar_importe()

    # Salir del programa
    elif opcion == "5":
        print("Gracias por utilizar TaxiTech.")
        break

    # Gestionar opciones incorrectas
    else:
        print("Opción incorrecta. Inténtalo de nuevo.")
