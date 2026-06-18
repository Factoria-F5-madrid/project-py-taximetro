<img width="11520" height="3456" alt="Copia de Banner notebooks" src="https://github.com/user-attachments/assets/1c187a02-2294-4f4b-ba84-63766c051a15" />

# 🚕 TaxiTech Solutions — Sistema de Taxímetro Digital

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Estado](https://img.shields.io/badge/Estado-En%20desarrollo-yellow)
![Sprint](https://img.shields.io/badge/Sprint-1-orange)
![Prioridad](https://img.shields.io/badge/Prioridad-Alta-red)

</div>

---

> **Proyecto:** `TTX-247` — Modernización del sistema de facturación en flota  
> **Cliente:** TaxiTech Solutions S.L. *(empresa de gestión de flotas de taxi, Madrid)*  
> **Equipo asignado:** Backend Squad — Nuevas incorporaciones   
> **Deadline:** Una semana a partir de la fecha de inicio del proyecto.

---

## 📩 Contexto del Encargo

El equipo de operaciones de **TaxiTech Solutions** lleva desde 2018 usando taxímetros físicos de la marca Hale modelo T200. El fabricante dejó de dar soporte en 2023 y los dispositivos están empezando a fallar en flota.

La dirección ha tomado la decisión de **migrar a un sistema 100% software** antes de Q3 2025. El CTO ha abierto este proyecto piloto para validar el concepto con un **prototipo funcional** antes de comprometer presupuesto con un proveedor externo.

Tu equipo ha sido asignado para desarrollar el prototipo.

---

## 🗣️ Briefing del Cliente

> *"Necesitamos algo que los taxistas puedan arrancar al inicio del turno y que calcule lo que le cuesta al pasajero en tiempo real. Cuando el taxi está parado en un semáforo, el contador sigue corriendo pero más despacio. En marcha, corre más rápido. Al llegar al destino, el taxista pulsa un botón, sale el total, y listo. Nos gustaría también poder ver un histórico de carreras del día. Si puede tener contraseña para que no lo toquen los pasajeros, mejor. Y si en el futuro se puede ver desde el móvil o una tablet en el taxi, perfecto."*  
> — Director de Operaciones, TaxiTech Solutions

**Tarifas vigentes (Zona EMT Madrid, junio 2025):**
- Taxi **parado o velocidad < 20 km/h**: `0.02 €/segundo`
- Taxi **en movimiento**: `0.05 €/segundo`

---

## 📋 Historias de Usuario

El equipo de producto ha desglosado el briefing en las siguientes historias. Están priorizadas por el cliente usando MoSCoW.

| ID | Historia | Prioridad |
|----|----------|-----------|
| US-01 | Como taxista, quiero iniciar una carrera con un solo comando para empezar a cobrar desde el momento de arranque | Must |
| US-02 | Como taxista, quiero cambiar el estado entre "parado" y "en movimiento" para que la tarifa se ajuste | Must |
| US-03 | Como taxista, quiero finalizar la carrera y ver el total en euros para cobrar al pasajero | Must |
| US-04 | Como taxista, quiero poder iniciar otra carrera sin cerrar el programa para no perder tiempo entre servicios | Must |
| US-05 | Como responsable de flota, quiero ver el histórico de carreras del día para cuadrar caja | Should |
| US-06 | Como técnico, quiero que el sistema genere logs de operación para diagnosticar errores en producción | Should |
| US-07 | Como técnico, quiero poder cambiar las tarifas en un fichero de configuración sin redeployar | Should |
| US-08 | Como responsable de flota, quiero que el sistema requiera contraseña para protegerlo de manipulaciones | Could |
| US-09 | Como taxista, quiero una interfaz visual con botones grandes para usarlo fácilmente con el móvil o tablet | Could |

---

## 📊 Fases de Entrega

El proyecto se divide en **4 fases incrementales**. Cada fase es un entregable autónomo y funcional.

### 🟢 Fase 1 — MVP Funcional (US-01 a US-04)

**Objetivo:** demostrar al cliente que el concepto funciona. CLI mínimo que cubra el flujo completo de una carrera.

Requisitos técnicos:
- Programa Python ejecutable desde terminal
- Mensaje de bienvenida con instrucciones de uso al arrancar
- Comando para iniciar carrera
- Comandos para cambiar entre estado `parado` y `en movimiento`
- Acumulación correcta de tarifa según el estado y el tiempo transcurrido
- Comando para finalizar la carrera y mostrar el total con 2 decimales
- Posibilidad de iniciar una nueva carrera sin cerrar el proceso

**Criterios de aceptación (definidos con el cliente):**
- [ ] `python taximetro.py` arranca sin errores en Python 3.10+
- [ ] El total acumulado es correcto: parado 10s → `0.20€`, movimiento 10s → `0.50€`
- [ ] El programa no termina al finalizar una carrera; pregunta si iniciar otra

---

### 🟡 Fase 2 — Observabilidad y Persistencia (US-05, US-06, US-07)

**Objetivo:** que el sistema sea mantenible y no pierda datos entre sesiones.

Requisitos técnicos:
- **Logging** estructurado con la librería estándar `logging`:
  - Niveles: `DEBUG` (cálculos internos), `INFO` (eventos de carrera), `WARNING/ERROR` (entradas inválidas)
  - Salida simultánea a consola y a fichero `taximetro.log`
- **Tests unitarios** con `pytest` o `unittest` (cobertura mínima de la lógica de tarifas)
- **Historial de carreras** persistido en `historial.csv` con columnas: `inicio`, `fin`, `duración_s`, `total_eur`
- **Configuración de tarifas** externalizada en `config.json` — modificable sin tocar el código

**Criterios de aceptación:**
- [ ] `pytest` pasa en verde con al menos 4 tests
- [ ] Tras cerrar y reabrir el programa, el historial sigue presente
- [ ] Cambiar `config.json` y reiniciar el programa aplica las nuevas tarifas
- [ ] El fichero `.log` recoge todos los eventos relevantes con timestamp

---

### 🟠 Fase 3 — Arquitectura y Experiencia de Usuario (US-08, US-09)

**Objetivo:** código mantenible a largo plazo y primera versión con interfaz visual.

Requisitos técnicos:
- **Refactorización a OOP**: al menos las clases `Taximetro`, `Trayecto` y `Tarifa` con responsabilidades bien separadas (principio SRP)
- **Autenticación**: pantalla de login con contraseña almacenada como hash (SHA-256 mínimo, bcrypt recomendado). Nunca texto plano
- **Interfaz gráfica** con `tkinter` (incluido en stdlib) o `PyQt5`:
  - Contador de euros en tiempo real (actualización ≤ 500ms)
  - Botones de acción grandes y visibles
  - Indicador de estado claro (parado / en movimiento)

**Criterios de aceptación:**
- [ ] La GUI no se congela al actualizar el contador (sin `time.sleep` en el hilo principal)
- [ ] La contraseña hasheada se guarda en disco; al reiniciar, se pide de nuevo
- [ ] Un revisor de código puede entender la responsabilidad de cada clase sin explicación

---

### 🔴 Fase 4 — Versión de Producción (US-10 + infraestructura)

**Objetivo:** entregable listo para desplegarse en los vehículos de la flota.

Requisitos técnicos:
- **Base de datos**: migración del historial CSV a `SQLite` usando `SQLAlchemy` como ORM
- **API REST** con Flask o Django REST Framework:
  - `POST /api/trayectos` — iniciar carrera
  - `PUT /api/trayectos/:id` — cambiar estado / finalizar
  - `GET /api/trayectos` — listar historial
- **Panel web** accesible desde navegador (puede ser HTML estático + fetch a la API)
- **Dockerización**: `Dockerfile` + `docker-compose.yml`; la app debe levantar con `docker-compose up` sin configuración adicional

**Criterios de aceptación:**
- [ ] `docker-compose up` levanta la app y es accesible en `http://localhost:5000`
- [ ] La API devuelve JSON válido con código HTTP correcto (200, 201, 404...)
- [ ] El historial sobrevive a un `docker-compose down && docker-compose up` (volumen persistente)

---

## 🛠️ Stack Técnico

```
Fase 1   Python 3.10+  ·  Git
Fase 2   logging  ·  pytest  ·  csv  ·  json
Fase 3   OOP  ·  bcrypt  ·  tkinter / PyQt5
Fase 4   SQLite  ·  SQLAlchemy  ·  Flask  ·  Docker
```

Gestión del proyecto: **Github Projects** (tablero Kanban, una columna por fase)

---

Convención de ramas:
```
main          → código estable, entregable al cliente
dev           → integración continua del equipo
feature/us-01 → una rama por historia de usuario
```

---

## 📦 Entregables por Fase

Cada fase debe entregarse con:

1. Repositorio de GitHub con el código fuente del proyecto.
2. **Demo** en directo
3. **Enlace al tablero Kanban** actualizado

---

## 📚 Recursos

### Documentación oficial
- [`time` — Python stdlib](https://docs.python.org/3/library/time.html)
- [`logging` — Python stdlib](https://docs.python.org/3/library/logging.html)
- [`unittest` — Python stdlib](https://docs.python.org/3/library/unittest.html)
- [`tkinter` — GUI básica](https://docs.python.org/3/library/tkinter.html)
- [Flask Quickstart](https://flask.palletsprojects.com/en/3.0.x/quickstart/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- [Docker — Get Started](https://docs.docker.com/get-started/)

### Guías de referencia
- [Real Python — OOP en Python](https://realpython.com/python3-object-oriented-programming/)
- [Real Python — pytest](https://realpython.com/pytest-python-testing/)
- [Real Python — Logging](https://realpython.com/python-logging/)
- [Conventional Commits](https://www.conventionalcommits.org/es/v1.0.0/) — formato de mensajes de commit

### Solución
[Solución proyecto](https://github.com/Factoria-F5-madrid/stn-taximetro)
