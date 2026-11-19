from taxi import Taxi
# US-05: Importamos la función para consultar el histórico
from historial import mostrar_historial_hoy

# Creamos nuestro objeto Taxi
taxi = Taxi()

# Mostramos el título de la aplicación
print("=============================")
print("          TAXITECH")
print("      TAXÍMETRO DIGITAL")
print("=============================")

# Mantenemos el programa funcionando
while True:

    # Opciones disponibles en TaxiTech
    print("\n--------- MENÚ ---------")
    print("1. Iniciar carrera / iniciar otra carrera")
    print("2. Taxi en movimiento")
    print("3. Taxi parado")
    print("4. Consultar importe")
    print("5. Finalizar carrera")
    print("6. Ver histórico de carreras de hoy")
    print("7. Salir")
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
    
    # US-03: Finalizar la carrera
    elif opcion == "5":
        taxi.finalizar_carrera()
    
    # US-05: Consultar las carreras guardadas hoy
    elif opcion == "6":
        mostrar_historial_hoy()

    
    # Salir de TaxiTech
    elif opcion == "7":

        # No permitimos salir si todavía hay una carrera
        if taxi.carrera_activa:
            print("Primero debes finalizar la carrera.")

        # Si no hay una carrera, cerramos la aplicación
        else:
            print("Gracias por utilizar TaxiTech.")
            break



    # Gestionar opciones incorrectas
    else:
        print("Opción incorrecta. Inténtalo de nuevo.")
