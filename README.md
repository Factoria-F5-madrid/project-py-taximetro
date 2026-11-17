# TaxiTech Solutions 🚕

**Proyecto:** TTX-247  
**Desarrollo:** Taxímetro digital para flota de taxis  
**Ubicación:** Madrid, España

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Fases](https://img.shields.io/badge/Fases-4%20implementadas-success)
![API](https://img.shields.io/badge/API-FastAPI-009688)
![Database](https://img.shields.io/badge/Database-SQLite-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)

## 1. Descripción del proyecto

TaxiTech Solutions es una aplicación de taxímetro digital desarrollada en Python para gestionar carreras, calcular tarifas, conservar el historial de servicios y facilitar la supervisión del sistema.

El proyecto evoluciona desde una primera versión funcional de consola hasta una arquitectura modular con interfaz gráfica, autenticación, API REST, base de datos relacional y despliegue mediante Docker.

## 2. Tarifas

| Estado del vehículo | Tarifa |
|---|---:|
| Parado o velocidad inferior a 20 km/h | 0,02 €/segundo |
| En movimiento | 0,05 €/segundo |

Las tarifas se configuran externamente mediante `config.json`.

## 3. Desarrollo por fases

### Fase 1. MVP funcional

- Inicio y finalización de carreras.
- Cambio entre estados parado y movimiento.
- Cálculo automático de tarifas.
- Encadenamiento de múltiples carreras.
- Interfaz de consola.

**Estado: completada.**

### Fase 2. Observabilidad y persistencia

- Registro de eventos mediante logs.
- Persistencia del historial en JSON.
- Conservación de fecha, duración e importe.
- Configuración externa de tarifas.
- Pruebas automatizadas.

**Estado: completada.**

### Fase 3. Arquitectura y experiencia de usuario

- Programación orientada a objetos.
- Separación de responsabilidades en módulos.
- Interfaz gráfica.
- Autenticación mediante contraseña.
- Organización del código para facilitar su mantenimiento.

**Estado: completada.**

### Fase 4. Preparación para producción

- Base de datos relacional SQLite.
- API REST desarrollada con FastAPI.
- Panel web de administración.
- Migración del historial JSON a SQLite.
- Despliegue mediante Docker Compose.
- Persistencia de datos mediante volúmenes Docker.

**Estado: implementada y verificada funcionalmente.**

## 4. Tecnologías utilizadas

- Python 3.10.
- FastAPI.
- Uvicorn.
- Pydantic.
- SQLite.
- JSON.
- HTML y JavaScript.
- Docker y Docker Compose.
- Git y GitHub.
- pytest.

## 5. Estructura del proyecto

```text
project-py-taximetro/
│
├── main.py
├── taximeter.py
├── api.py
├── config.json
├── requirements.txt
├── Dockerfile
├── compose.yaml
├── .dockerignore
├── .gitignore
├── README.md
│
├── taximetro/
│   ├── __init__.py
│   ├── carrera.py
│   ├── taximetro.py
│   ├── configuracion.py
│   ├── persistencia.py
│   ├── persistencia_sqlite.py
│   ├── autenticacion.py
│   └── logging_config.py
│
├── interfaces/
│   ├── __init__.py
│   ├── consola.py
│   └── grafica.py
│
├── templates/
│   └── admin.html
│
├── tests/
│   ├── test_taximeter.py
│   └── test_autenticacion.py
│
├── data/
│   ├── historial.json
│   └── taxitech.db
│
└── logs/
    └── taximetro.log
```

Los directorios `data/` y `logs/` contienen información persistente y se excluyen del control de versiones.

## 6. Instalación y ejecución local

### Requisitos

- Python 3.10 o superior.
- Git.

### Clonar el repositorio

```powershell
git clone https://github.com/superkaiker/project-py-taximetro.git
cd project-py-taximetro
```

### Crear y activar entorno virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Instalar dependencias

```powershell
pip install -r requirements.txt
```

### Ejecutar la aplicación

Consola:

```powershell
python .\main.py
```

Interfaz gráfica:

```powershell
python .\interfaces\grafica.py
```

API REST:

```powershell
uvicorn api:app --reload
```

## 7. API REST

La API permite gestionar carreras y consultar el historial.

| Método | Endpoint | Funcionalidad |
|---|---|---|
| GET | `/health` | Comprobar estado del servicio |
| POST | `/api/carreras` | Iniciar carrera |
| PATCH | `/api/carreras/estado` | Cambiar estado |
| POST | `/api/carreras/finalizar` | Finalizar y guardar carrera |
| GET | `/api/carreras` | Consultar historial |

Las operaciones de gestión de carreras y consulta del historial están protegidas mediante autenticación HTTP Basic.

### Documentación interactiva

Con el servidor iniciado:

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI: `http://localhost:8000/openapi.json`
- Panel web: `http://localhost:8000/admin`
- Estado del servicio: `http://localhost:8000/health`

## 8. Persistencia de datos

El sistema utiliza SQLite como base de datos relacional para conservar las carreras finalizadas.

La aplicación inicializa la base de datos y permite migrar los registros históricos almacenados previamente en JSON.

Cada carrera conserva:

- Fecha y hora de inicio.
- Duración en segundos.
- Importe calculado en euros.

El proyecto mantiene también el historial JSON original como fuente de migración.

## 9. Sistema de logs

Los registros de operación se almacenan en:

```text
logs/taximetro.log
```

Se registran eventos como:

- Inicio y parada del servicio.
- Migración de datos.
- Cambios de estado.
- Finalización de carreras.
- Errores durante las operaciones.

## 10. Despliegue con Docker

Docker Compose permite construir y ejecutar el servicio con un único comando.

### Iniciar la aplicación

```powershell
docker compose up -d --build
```

### Consultar el estado

```powershell
docker compose ps
```

### Consultar los logs

```powershell
docker compose logs -f
```

### Reiniciar el servicio

```powershell
docker compose restart
```

### Detener el servicio

```powershell
docker compose down
```

Los directorios `data/` y `logs/` se montan como volúmenes persistentes para conservar la información entre reinicios del contenedor.

## 11. Pruebas automatizadas

El proyecto dispone de pruebas automatizadas mediante pytest.

Ejecución:

```powershell
python -m pytest -q
```

**Último resultado verificado: 26 pruebas superadas.**

```text
26 passed in 1.35s
```

También se han realizado pruebas funcionales de la API y del despliegue Docker, incluyendo:

- Inicio y finalización de carreras.
- Validación de estados.
- Control de carreras activas.
- Persistencia de registros en SQLite.
- Consulta del historial mediante API.
- Acceso autenticado al panel web.
- Reinicio del contenedor conservando los datos.

## 12. Demostración funcional

Durante las pruebas de producción local se verificó:

- Servicio Docker operativo en el puerto 8000.
- API REST accesible.
- Panel web de administración operativo.
- 24 carreras recuperadas desde el historial.
- Última carrera registrada con un importe de 10,38 €.
- Persistencia del historial después de reiniciar el contenedor.

## 13. Entregables

Cada fase contempla:

- Código fuente actualizado en GitHub.
- Demostración funcional.
- Pruebas correspondientes.
- Actualización del tablero Kanban de GitHub Projects.

## 14. Repositorio y documentación

- [Repositorio TaxiTech](https://github.com/superkaiker/project-py-taximetro)
- [Documentación Python](https://docs.python.org/3/)
- [Documentación FastAPI](https://fastapi.tiangolo.com/)
- [Documentación Docker](https://docs.docker.com/)

---

**TaxiTech Solutions | Proyecto TTX-247**

Desarrollo incremental de un taxímetro digital en Python.