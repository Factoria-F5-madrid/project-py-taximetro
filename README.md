# TaxiTech Solutions 🚕

**Proyecto:** TTX-247  
**Desarrollo:** Taxímetro digital para flota de taxis  
**Ubicación:** Madrid, España

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Estado](https://img.shields.io/badge/Estado-Fase%203%20en%20desarrollo-orange)
![Fases](https://img.shields.io/badge/Fases-1%20y%202%20completadas-success)
![Prioridad](https://img.shields.io/badge/Prioridad-Alta-red)

## 1. Contexto del proyecto

TaxiTech Solutions es una empresa de transporte urbano que necesita modernizar el sistema de tarificación de su flota de taxis en Madrid.

Actualmente, la empresa utiliza un sistema de taxímetro que necesita mejoras en su funcionamiento, mantenimiento y capacidad de supervisión.

El objetivo del proyecto es desarrollar una aplicación de taxímetro digital en Python que permita calcular automáticamente el coste de cada carrera, registrar los servicios realizados y facilitar el mantenimiento del sistema.

El desarrollo se organiza en diferentes fases, comenzando por un MVP funcional de consola y evolucionando hacia una solución más completa.

### Tarifas oficiales de referencia

Zona EMT Madrid, junio de 2025:

| Estado del vehículo | Tarifa |
|---|---:|
| Parado o velocidad inferior a 20 km/h | 0,02 €/segundo |
| En movimiento | 0,05 €/segundo |

### Necesidad del cliente

El sistema debe permitir iniciar y finalizar carreras, cambiar entre los estados de parado y movimiento y calcular automáticamente el importe correspondiente.

Además, debe facilitar la consulta del historial de servicios, conservar los datos entre ejecuciones y registrar eventos para facilitar el diagnóstico de posibles incidencias.

## 2. Historias de usuario

### Funcionalidades principales

| ID | Historia de usuario | Prioridad |
|---|---|---|
| US-01 | Como taxista, quiero iniciar una carrera con un comando para comenzar a cobrar al pasajero. | Must |
| US-02 | Como taxista, quiero cambiar el estado del vehículo entre parado y movimiento para aplicar la tarifa correspondiente. | Must |
| US-03 | Como taxista, quiero finalizar una carrera y visualizar el importe total en euros. | Must |
| US-04 | Como taxista, quiero iniciar una nueva carrera sin cerrar el programa. | Must |

### Funcionalidades adicionales

| ID | Historia de usuario | Prioridad |
|---|---|---|
| US-05 | Como gestor de flota, quiero consultar el historial diario de carreras para realizar la conciliación de caja. | Should |
| US-06 | Como técnico, quiero disponer de registros de operación para diagnosticar errores. | Should |
| US-07 | Como técnico, quiero modificar las tarifas mediante un archivo de configuración sin necesidad de volver a desplegar la aplicación. | Should |
| US-08 | Como gestor, quiero proteger el acceso mediante contraseña. | Could |
| US-09 | Como taxista, quiero disponer de una interfaz visual con botones grandes para utilizarla desde una tablet o dispositivo móvil. | Could |

## 3. Plan de desarrollo por fases

### Fase 1. MVP funcional

**Objetivo:** desarrollar una primera versión operativa del taxímetro mediante una interfaz de consola.

Funcionalidades:
- Inicio de una carrera mediante un comando.
- Cálculo continuo del importe.
- Cambio entre estado parado y movimiento.
- Aplicación automática de las tarifas correspondientes.
- Finalización de la carrera y visualización del importe.
- Posibilidad de encadenar varias carreras sin cerrar el programa.

**Estado:** completada.

### Fase 2. Observabilidad y persistencia

**Objetivo:** mejorar la capacidad de supervisión y conservación de información del sistema.

Funcionalidades:
- Registro de eventos relevantes mediante logs estructurados.
- Registro del inicio y finalización del programa.
- Registro de cambios de estado y finalización de carreras.
- Registro de errores para facilitar el diagnóstico.
- Persistencia del historial de carreras en disco.
- Conservación de fecha, duración e importe de cada servicio.
- Consulta del historial diario y del total recaudado.
- Configuración externa de las tarifas mediante un archivo JSON.
- Pruebas automatizadas del cálculo y de las funcionalidades principales.

**Estado:** implementada y verificada mediante pruebas automatizadas.

### Fase 3. Programación orientada a objetos y experiencia de usuario

**Objetivo:** mejorar la organización interna y la experiencia de utilización.

Funcionalidades previstas:
- Separación de responsabilidades y refactorización de la arquitectura.
- Organización del código en módulos especializados.
- Coordinación de la lógica de negocio mediante clases.
- Protección mediante contraseña.
- Interfaz gráfica con botones grandes.
- Adaptación de la experiencia de usuario para tablets y dispositivos móviles.

**Estado:** en desarrollo.

La refactorización y separación de responsabilidades ya se han iniciado mediante una arquitectura modular. La protección mediante contraseña y la interfaz gráfica continúan pendientes.

### Fase 4. Preparación para producción

**Objetivo:** evolucionar hacia una solución preparada para un entorno de producción.

Funcionalidades previstas:
- Integración con una base de datos relacional.
- Desarrollo de una API REST.
- Panel web de administración.
- Despliegue mediante un único comando.

**Estado:** pendiente.

## 4. Instalación y ejecución

### Requisitos

- Python 3.10 o superior.
- Git.
- Visual Studio Code (recomendado).

El proyecto utiliza actualmente la biblioteca estándar de Python, por lo que no necesita instalar dependencias externas.

### Clonar el repositorio

```bash
git clone https://github.com/superkaiker/project-py-taximetro.git
cd project-py-taximetro
```

### Crear el entorno virtual

En Windows PowerShell:

```powershell
python -m venv .venv
```

### Activar el entorno virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

### Ejecutar la aplicación

El punto de entrada principal recomendado es:

```powershell
python .\main.py
```

Se mantiene `taximeter.py` como punto de entrada compatible con la estructura anterior:

```powershell
python .\taximeter.py
```

Ambos comandos permiten acceder a la misma aplicación de consola.

## 5. Uso de la aplicación

La aplicación dispone de una interfaz de consola interactiva.

### Comandos disponibles

| Comando | Descripción |
|---|---|
| `iniciar` | Inicia una nueva carrera. |
| `mover` | Cambia el estado del vehículo a movimiento. |
| `parar` | Cambia el estado del vehículo a parado. |
| `finalizar` | Finaliza la carrera y muestra el importe total. |
| `historial` | Muestra las carreras del día y el total recaudado. |
| `ayuda` | Muestra los comandos disponibles. |
| `salir` | Finaliza la aplicación. |

### Ejemplo de utilización

```text
> iniciar
Carrera iniciada. Estado inicial: parado.

> mover
Estado actualizado: movimiento.

> parar
Estado actualizado: parado.

> finalizar
Total de la carrera: X.XX €
Carrera guardada en el historial.

> historial
Historial de carreras de hoy:
...

Total recaudado: X.XX €
```

Los importes del ejemplo son ilustrativos. El resultado real depende de la duración de cada estado.

## 6. Configuración de tarifas

Las tarifas se encuentran en el archivo `config.json`, situado en la raíz del proyecto.

Contenido actual:

```json
{
    "tarifa_parado": 0.02,
    "tarifa_movimiento": 0.05
}
```

Las cantidades representan euros por segundo.

Para modificar las tarifas basta con editar los valores del archivo de configuración. La aplicación carga la configuración al iniciarse, sin necesidad de modificar el código fuente.

Si el archivo no existe o contiene valores inválidos, el sistema utiliza las tarifas predeterminadas.

## 7. Persistencia de datos

El sistema conserva el historial de carreras finalizadas en:

```text
data/historial.json
```

Cada carrera almacena información como:
- Fecha y hora de registro.
- Duración de la carrera.
- Importe total.

Los datos se guardan en disco de forma incremental y permanecen disponibles después de cerrar y volver a ejecutar el programa.

El directorio `data/` se crea automáticamente cuando es necesario.

## 8. Sistema de logs

Los registros de operación se almacenan en:

```text
logs/taximetro.log
```

El sistema utiliza registros estructurados en formato JSON para facilitar su lectura y posterior procesamiento.

Los eventos registrados incluyen:
- Inicio y finalización del programa.
- Carga de tarifas.
- Cambios de estado del vehículo.
- Finalización de carreras.
- Errores e incidencias.

El archivo puede consultarse externamente mientras el programa está en funcionamiento.

El directorio `logs/` se crea automáticamente.

## 9. Pruebas automatizadas

El proyecto incluye pruebas automatizadas mediante `unittest`, la biblioteca de pruebas integrada en Python.

Para ejecutar la batería completa:

```powershell
python -m unittest discover -s tests -v
```

Para comprobar la sintaxis de los módulos:

```powershell
python -m compileall .\taximetro .\interfaces .\main.py .\taximeter.py
```

**Estado de las pruebas:** 18 pruebas superadas.

Las pruebas cubren funcionalidades relacionadas con:
- Cálculo de tarifas.
- Cambios de estado.
- Persistencia del historial.
- Validación de registros JSON.
- Lectura de configuración.
- Comportamiento ante configuraciones inexistentes o incorrectas.
- Inicio y finalización de carreras.
- Gestión de carreras activas.
- Liberación del taxímetro después de finalizar una carrera.
- Posibilidad de iniciar nuevas carreras.

## 10. Estructura del proyecto

La aplicación está organizada en módulos para separar la lógica de negocio, la configuración, la persistencia, los registros y la interfaz de usuario.

```text
project-py-taximetro/
│
├── main.py
├── taximeter.py
├── config.json
├── .gitignore
├── README.md
│
├── taximetro/
│   ├── __init__.py
│   ├── carrera.py
│   ├── taximetro.py
│   ├── configuracion.py
│   ├── persistencia.py
│   └── logging_config.py
│
├── interfaces/
│   └── consola.py
│
├── tests/
│   └── test_taximeter.py
│
├── data/
│   └── historial.json
│
└── logs/
    └── taximetro.log
```

### Responsabilidades de los módulos

| Módulo | Responsabilidad |
|---|---|
| `main.py` | Punto de entrada principal de la aplicación. |
| `taximeter.py` | Compatibilidad con los imports y el punto de entrada anteriores. |
| `taximetro/carrera.py` | Gestión del estado, duración y cálculo económico de una carrera. |
| `taximetro/taximetro.py` | Coordinación de las operaciones del taxímetro y las carreras activas. |
| `taximetro/configuracion.py` | Lectura y validación de las tarifas. |
| `taximetro/persistencia.py` | Almacenamiento y recuperación del historial. |
| `taximetro/logging_config.py` | Configuración del sistema de registros. |
| `interfaces/consola.py` | Interacción con el usuario mediante comandos de consola. |
| `tests/test_taximeter.py` | Pruebas automatizadas del funcionamiento. |

Los directorios `data/` y `logs/` se generan durante la ejecución. Sus contenidos están excluidos del control de versiones mediante `.gitignore`.

## 11. Tecnologías utilizadas

- **Python:** lenguaje principal de desarrollo.
- **Git:** control de versiones.
- **GitHub:** alojamiento y gestión del repositorio.
- **JSON:** configuración de tarifas, persistencia de datos y registros estructurados.
- **unittest:** pruebas automatizadas.
- **Logging:** registro de eventos y diagnóstico.

## 12. Entregables del proyecto

Cada fase contempla los siguientes entregables:
- Código fuente actualizado en GitHub.
- Demostración funcional de las funcionalidades implementadas.
- Actualización del tablero Kanban del proyecto.

El repositorio contiene el código fuente y las pruebas correspondientes al estado actual del desarrollo.

## 13. Restricciones y criterios del proyecto

- El lenguaje de programación principal será Python.
- El control de versiones se realizará mediante Git y GitHub.
- La gestión de tareas se realizará mediante GitHub Projects.
- Las funcionalidades se desarrollarán de forma incremental.
- Se priorizará el cumplimiento de las historias de usuario según su prioridad.
- Las funcionalidades no implementadas se mantendrán identificadas como pendientes.

## 14. Recursos y referencias

- [Repositorio del proyecto](https://github.com/superkaiker/project-py-taximetro)
- [Documentación oficial de Python](https://docs.python.org/3/)
- [Documentación de Git](https://git-scm.com/doc)
- [Documentación de GitHub Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects)

---

**TaxiTech Solutions | Proyecto TTX-247**

Desarrollo incremental de un sistema de taxímetro digital en Python.