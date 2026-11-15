from taximetro.tarifas import ESTADO_PARADO, calcular_tramo


class Carrera:
    def __init__(self, hora_inicio: float) -> None:
        self.hora_inicio = hora_inicio
        self.estado = ESTADO_PARADO
        self.hora_ultimo_cambio = hora_inicio
        self.importe = 0.0

    def cerrar_tramo(self, ahora: float) -> None:
        segundos = ahora - self.hora_ultimo_cambio
        self.importe += calcular_tramo(self.estado, segundos)
        self.hora_ultimo_cambio = ahora

    def cambiar_estado(self, nuevo_estado: str, ahora: float) -> None:
        self.cerrar_tramo(ahora)
        self.estado = nuevo_estado

    def finalizar(self, ahora: float) -> float:
        self.cerrar_tramo(ahora)
        return self.importe
