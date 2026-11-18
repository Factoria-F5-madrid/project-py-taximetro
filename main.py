# main.py (en la raíz del proyecto)
from app.taximetro import TaximetroMVP


def main():
    app = TaximetroMVP()
    app.ejecutar()  # O el método principal que arranque el bucle del taxímetro

if __name__ == "__main__":
    main()


