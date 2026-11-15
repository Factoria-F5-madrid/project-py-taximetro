TARIFA_PARADO = 0.02

TARIFA_MOVIMIENTO = 0.05

ESTADO_PARADO = "parado"

ESTADO_MOVIMIENTO = "movimiento"

def calcular_tramo(estado: str, segundos: float) -> float:
    if estado == ESTADO_MOVIMIENTO:
        return segundos * TARIFA_MOVIMIENTO
    return segundos * TARIFA_PARADO
