from taxi import Taxi

def user_loggage():
    print("Add your Loggage")
    print("Now See you Issue")
    print("Now See you Issue number")

taxi = Taxi()

print("=============================")
print("      TAXÍMETRO DIGITAL")
print("=============================")

# Mantenemos la aplicación funcionando en bucle hasta que el usuario decida salir
while True:

    # Mostramos el menú provisional
    print("\n1. Iniciar carrera")
    print("2. Salir")

    # Pedimos al usuario que elija una opción
    opcion = input("Selecciona una opción: ")

    # Primera opción: iniciar carrera
    if opcion == "1":
        taxi.iniciar_carrera()

    # Segunda opción: salir
    elif opcion == "2":
        print("Gracias por utilizar TaxiTech.")
        break

    # Si el usuario introduce otra opción
    else:
        print("Opción incorrecta.")
