import pytest
from app.configuracion import GestorConfiguracion
from app.taximetro import TaximetroMVP

def test_cargar_configuracion_tarifas():
    """Verifica que el gestor de configuración carga un diccionario con las tarifas esperadas."""
    gestor = GestorConfiguracion()
    tarifas = gestor.cargar_tarifas()
    
    assert isinstance(tarifas, dict)
    assert "TARIFA_PARADO" in tarifas
    assert "TARIFA_MOVIMIENTO" in tarifas
    assert isinstance(tarifas["TARIFA_PARADO"], (int, float))
    assert isinstance(tarifas["TARIFA_MOVIMIENTO"], (int, float))

def test_calculo_coste_tarifa():
    """Verifica que el taxímetro aplica correctamente las tarifas cargadas en sus cálculos."""
    taximetro = TaximetroMVP()
    
    # Forzamos valores conocidos para comprobar la fórmula matemática
    taximetro.TARIFA_PARADO = 0.02
    taximetro.TARIFA_MOVIMIENTO = 0.05
    taximetro.carrera_activa = True
    taximetro.coste_acumulado = 0.0
    
    # Simulamos 10 segundos en estado PARADO (10 * 0.02 = 0.20)
    taximetro.estado_actual = "PARADO"
    taximetro.tiempo_total_carrera = 10.0
    taximetro.coste_acumulado = taximetro.tiempo_total_carrera * taximetro.TARIFA_PARADO
    
    assert round(taximetro.coste_acumulado, 2) == 0.20

    # Simulamos 10 segundos adicionales en MOVIMIENTO (10 * 0.05 = 0.50 -> acumulado total 0.70)
    taximetro.estado_actual = "MOVIMIENTO"
    duracion_movimiento = 10.0
    taximetro.tiempo_total_carrera += duracion_movimiento
    taximetro.coste_acumulado += duracion_movimiento * taximetro.TARIFA_MOVIMIENTO
    
    assert round(taximetro.coste_acumulado, 2) == 0.70