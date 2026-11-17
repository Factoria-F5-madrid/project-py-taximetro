
"""Interfaz gráfica TAXITECH NEO//DRIVE para TaxiTech Solutions.

Interfaz Tkinter del MVP TTX-247.
Mantiene el motor de cálculo, las tarifas y la persistencia existentes.
"""

import logging
import math
import tkinter as tk
from time import monotonic
from tkinter import messagebox, ttk

from taximetro.autenticacion import autenticar_grafica
from taximetro.configuracion import cargar_tarifas
from taximetro.logging_config import configurar_logging
from taximetro.persistencia import cargar_historial, guardar_carrera
from taximetro.taximetro import Taximetro


logger = logging.getLogger(__name__)


class VentanaTaximetro:
    """Ventana principal TAXITECH NEO//DRIVE."""

    FONDO = "#0B0F0D"
    PANEL = "#151C18"
    PANEL2 = "#1E2822"
    BORDE = "#2E3B32"
    VERDE = "#C8FF00"
    VERDE_OSCURO = "#263500"
    AMARILLO = "#FFD43B"
    BLANCO = "#F2F5F0"
    GRIS = "#9AA69D"
    ROJO = "#FF6262"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("TAXITECH NEO//DRIVE | TTX-247")
        self.root.geometry("1720x900")
        self.root.minsize(1280, 760)
        self.root.configure(bg=self.FONDO)

        tarifa_parado, tarifa_movimiento = cargar_tarifas()
        self.tarifa_parado = tarifa_parado
        self.tarifa_movimiento = tarifa_movimiento

        self.taximetro = Taximetro(
            tarifa_parado=tarifa_parado,
            tarifa_movimiento=tarifa_movimiento,
        )

        self.carrera_pendiente_guardar = None

        self._configurar_estilos()
        self._crear_interfaz()
        self._actualizar_controles()
        self._cargar_historial()
        self._actualizar_reloj()

        self.root.protocol("WM_DELETE_WINDOW", self._cerrar)

    # ---------------------------------------------------------
    # ESTILOS
    # ---------------------------------------------------------

    def _configurar_estilos(self) -> None:
        estilo = ttk.Style(self.root)
        estilo.theme_use("clam")

        estilo.configure(
            "Treeview",
            background=self.PANEL2,
            foreground=self.BLANCO,
            fieldbackground=self.PANEL2,
            borderwidth=0,
            rowheight=30,
            font=("Segoe UI", 9),
        )

        estilo.configure(
            "Treeview.Heading",
            background=self.PANEL,
            foreground=self.VERDE,
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            padding=(10, 9),
        )

        estilo.map(
            "Treeview",
            background=[("selected", self.VERDE_OSCURO)],
            foreground=[("selected", self.VERDE)],
        )

        estilo.configure(
            "Vertical.TScrollbar",
            background=self.PANEL2,
            troughcolor=self.PANEL,
            borderwidth=0,
        )

    # ---------------------------------------------------------
    # TEXTURA DE CARBONO
    # ---------------------------------------------------------

    def _aplicar_textura_carbono(self, panel: tk.Frame) -> None:
        """Dibuja una fibra de carbono tipo sarga, fina y sin efecto pixelado."""

        color_base = panel.cget("bg")
        textura = tk.Canvas(
            panel,
            bg=color_base,
            highlightthickness=0,
            bd=0,
            takefocus=0,
        )
        textura.place(
            x=1,
            y=1,
            relwidth=1,
            relheight=1,
            width=-2,
            height=-2,
        )
        tk.Misc.lower(textura)

        def dibujar(_evento=None) -> None:
            textura.delete("carbono")
            ancho = textura.winfo_width()
            alto = textura.winfo_height()
            paso = 12
            grosor = 2

            textura.configure(bg=color_base)

            for y in range(-paso, alto + paso, paso):
                for x in range(-paso, ancho + paso, paso):
                    alterna = ((x // paso) + (y // paso)) % 2 == 0
                    if alterna:
                        color_luz = "#202A24"
                        color_sombra = "#111713"
                        textura.create_line(
                            x, y + paso, x + paso, y,
                            fill=color_luz, width=grosor, tags="carbono"
                        )
                        textura.create_line(
                            x + 2, y + paso, x + paso + 2, y,
                            fill=color_sombra, width=1, tags="carbono"
                        )
                    else:
                        color_luz = "#1D2721"
                        color_sombra = "#121814"
                        textura.create_line(
                            x, y, x + paso, y + paso,
                            fill=color_luz, width=grosor, tags="carbono"
                        )
                        textura.create_line(
                            x + 2, y, x + paso + 2, y + paso,
                            fill=color_sombra, width=1, tags="carbono"
                        )

        textura.bind("<Configure>", dibujar)
        panel.after_idle(dibujar)

    # ---------------------------------------------------------
    # ESTRUCTURA PRINCIPAL
    # ---------------------------------------------------------

    def _crear_interfaz(self) -> None:
        principal = tk.Frame(
            self.root,
            bg=self.FONDO,
            padx=22,
            pady=16,
        )
        principal.pack(fill="both", expand=True)

        principal.columnconfigure(0, weight=1)
        principal.rowconfigure(3, weight=0)
        principal.rowconfigure(4, weight=1)

        self._crear_cabecera(principal)
        self._crear_panel_principal(principal)
        self._crear_tarifas(principal)
        self._crear_controles(principal)
        self._crear_historial(principal)

        pie = tk.Label(
            principal,
            text="TAXITECH SOLUTIONS   /   NEO DRIVE   /   TTX-247",
            bg=self.FONDO,
            fg=self.GRIS,
            font=("Segoe UI", 8, "bold"),
        )
        pie.grid(row=5, column=0, sticky="ew", pady=(10, 0))

    def _crear_cabecera(self, parent: tk.Widget) -> None:
        cabecera = tk.Frame(parent, bg=self.FONDO)
        cabecera.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        cabecera.columnconfigure(0, weight=1)

        identidad = tk.Frame(cabecera, bg=self.FONDO)
        identidad.grid(row=0, column=0, sticky="w")

        tk.Label(
            identidad,
            text="TT",
            bg=self.VERDE,
            fg=self.FONDO,
            font=("Segoe UI", 18, "bold"),
            width=3,
            pady=5,
        ).pack(side="left", padx=(0, 12))

        textos = tk.Frame(identidad, bg=self.FONDO)
        textos.pack(side="left")

        tk.Label(
            textos,
            text="TAXITECH NEO//DRIVE",
            bg=self.FONDO,
            fg=self.BLANCO,
            font=("Segoe UI", 21, "bold"),
        ).pack(anchor="w")

        tk.Label(
            textos,
            text="SMART TAXIMETER CONTROL SYSTEM",
            bg=self.FONDO,
            fg=self.GRIS,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w")

        tk.Label(
            cabecera,
            text="TTX-247   /   MADRID",
            bg=self.PANEL,
            fg=self.VERDE,
            font=("Segoe UI", 9, "bold"),
            padx=18,
            pady=12,
        ).grid(row=0, column=1, sticky="e")

    # ---------------------------------------------------------
    # PANEL CENTRAL: OPERACIÓN + INSTRUMENTACIÓN
    # ---------------------------------------------------------

    def _crear_panel_principal(self, parent: tk.Widget) -> None:
        """Distribución híbrida: lectura profesional y estética cockpit."""
        zona = tk.Frame(parent, bg=self.FONDO)
        zona.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        zona.columnconfigure(0, weight=7)
        zona.columnconfigure(1, weight=4)

        self._crear_hero(zona)
        self._crear_cockpit(zona)

    def _crear_hero(self, parent: tk.Widget) -> None:
        """Panel operativo: importe, duración y tarifa, sin imagen decorativa."""
        panel = tk.Frame(
            parent,
            bg=self.PANEL,
            highlightbackground=self.BORDE,
            highlightthickness=1,
            padx=22,
            pady=18,
        )
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self._aplicar_textura_carbono(panel)
        panel.columnconfigure(0, weight=1)

        cabecera = tk.Frame(panel, bg=self.PANEL)
        cabecera.grid(row=0, column=0, sticky="ew")
        cabecera.columnconfigure(0, weight=1)

        tk.Label(
            cabecera,
            text="TAXÍMETRO PROFESIONAL  /  TTX-247",
            bg=self.PANEL,
            fg=self.GRIS,
            font=("Segoe UI", 9, "bold"),
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            cabecera,
            text="NEO//DRIVE",
            bg=self.PANEL,
            fg=self.VERDE,
            font=("Segoe UI", 9, "bold"),
        ).grid(row=0, column=1, sticky="e")

        tk.Frame(panel, bg=self.BORDE, height=1).grid(
            row=1, column=0, sticky="ew", pady=(13, 16)
        )

        tk.Label(
            panel,
            text="IMPORTE DE CARRERA",
            bg=self.PANEL,
            fg=self.GRIS,
            font=("Segoe UI", 10, "bold"),
        ).grid(row=2, column=0, sticky="w")

        self.importe_var = tk.StringVar(value="0,00 €")
        tk.Label(
            panel,
            textvariable=self.importe_var,
            bg=self.PANEL,
            fg=self.AMARILLO,
            font=("Segoe UI", 54, "bold"),
            anchor="w",
        ).grid(row=3, column=0, sticky="w", pady=(0, 12))

        franja = tk.Frame(panel, bg=self.PANEL2, padx=14, pady=12)
        franja.grid(row=4, column=0, sticky="ew", pady=(2, 0))
        franja.columnconfigure((0, 1), weight=1)

        self.duracion_var = tk.StringVar(value="00:00:00")
        self.tarifa_activa_var = tk.StringVar(value="A la espera de carrera")

        tk.Label(
            franja,
            text="DURACIÓN",
            bg=self.PANEL2,
            fg=self.GRIS,
            font=("Segoe UI", 8, "bold"),
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            franja,
            textvariable=self.duracion_var,
            bg=self.PANEL2,
            fg=self.BLANCO,
            font=("Segoe UI", 19, "bold"),
        ).grid(row=1, column=0, sticky="w", pady=(3, 0))

        tk.Label(
            franja,
            text="TARIFA ACTIVA",
            bg=self.PANEL2,
            fg=self.GRIS,
            font=("Segoe UI", 8, "bold"),
        ).grid(row=0, column=1, sticky="w", padx=(18, 0))

        tk.Label(
            franja,
            textvariable=self.tarifa_activa_var,
            bg=self.PANEL2,
            fg=self.VERDE,
            font=("Segoe UI", 12, "bold"),
            wraplength=250,
            justify="left",
        ).grid(row=1, column=1, sticky="w", padx=(18, 0), pady=(3, 0))

        tk.Label(
            panel,
            text="CÁLCULO AUTOMÁTICO  ·  ACTUALIZACIÓN EN TIEMPO REAL",
            bg=self.PANEL,
            fg=self.GRIS,
            font=("Segoe UI", 8, "bold"),
        ).grid(row=5, column=0, sticky="w", pady=(14, 0))

    def _crear_cockpit(self, parent: tk.Widget) -> None:
        """Indicador visual de estado real de la carrera, sin datos inventados."""
        panel = tk.Frame(
            parent,
            bg=self.PANEL,
            highlightbackground=self.BORDE,
            highlightthickness=1,
            padx=18,
            pady=14,
        )
        panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self._aplicar_textura_carbono(panel)

        tk.Label(
            panel,
            text="ESTADO DE OPERACIÓN",
            bg=self.PANEL,
            fg=self.GRIS,
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w")

        self.canvas = tk.Canvas(
            panel,
            width=250,
            height=220,
            bg=self.PANEL,
            highlightthickness=0,
        )
        self.canvas.pack(expand=True, pady=(4, 0))
        self._dibujar_indicador()

        self.estado_var = tk.StringVar(value="SIN ACTIVIDAD")
        self.etiqueta_estado = tk.Label(
            panel,
            textvariable=self.estado_var,
            bg=self.PANEL2,
            fg=self.BLANCO,
            font=("Segoe UI", 12, "bold"),
            padx=12,
            pady=9,
        )
        self.etiqueta_estado.pack(fill="x", pady=(2, 0))

    def _dibujar_indicador(self) -> None:
        """Dibuja la instrumentación de estado sin representar datos ficticios."""

        c = self.canvas
        c.delete("all")

        color = self._color_estado()
        centro_x = 125
        centro_y = 105

        c.create_oval(
            28,
            8,
            222,
            202,
            outline=self.BORDE,
            width=2,
        )

        c.create_oval(
            39,
            19,
            211,
            191,
            outline=color,
            width=3,
        )

        c.create_arc(
            39,
            19,
            211,
            191,
            start=135,
            extent=270,
            style="arc",
            outline=color,
            width=5,
        )

        for angulo in range(0, 360, 15):
            radianes = math.radians(angulo)
            radio_exterior = 83
            radio_interior = 74

            x1 = centro_x + radio_interior * math.cos(radianes)
            y1 = centro_y + radio_interior * math.sin(radianes)
            x2 = centro_x + radio_exterior * math.cos(radianes)
            y2 = centro_y + radio_exterior * math.sin(radianes)

            c.create_line(
                x1,
                y1,
                x2,
                y2,
                fill=self.GRIS,
                width=1,
            )

        c.create_oval(
            62,
            42,
            188,
            168,
            fill=self.PANEL2,
            outline=self.BORDE,
            width=2,
        )

        c.create_text(
            centro_x,
            79,
            text="ESTADO",
            fill=self.GRIS,
            font=("Segoe UI", 9, "bold"),
        )

        c.create_text(
            centro_x,
            108,
            text=self._texto_estado(),
            fill=color,
            font=("Segoe UI", 13, "bold"),
        )

        c.create_text(
            centro_x,
            135,
            text="TTX-247",
            fill=self.BLANCO,
            font=("Segoe UI", 9),
        )

        c.create_text(
            centro_x,
            215,
            text="SYSTEM MONITOR",
            fill=self.GRIS,
            font=("Segoe UI", 7, "bold"),
        )

    def _color_estado(self) -> str:
        carrera = self.taximetro.carrera_actual

        if carrera is None:
            return self.GRIS

        if carrera.estado == "movimiento":
            return self.VERDE

        return self.AMARILLO

    def _texto_estado(self) -> str:
        carrera = self.taximetro.carrera_actual

        if carrera is None:
            if self.carrera_pendiente_guardar is not None:
                return "FINALIZADA"
            return "INACTIVO"

        if carrera.estado == "movimiento":
            return "MOVIMIENTO"

        return "PARADO"

    # ---------------------------------------------------------
    # TARIFAS
    # ---------------------------------------------------------

    def _crear_tarifas(self, parent: tk.Widget) -> None:
        contenedor = tk.Frame(parent, bg=self.FONDO)
        contenedor.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        contenedor.columnconfigure((0, 1), weight=1)

        self._crear_tarjeta_tarifa(
            contenedor,
            0,
            "TARIFA EN PARADO",
            self.tarifa_parado,
            self.AMARILLO,
        )

        self._crear_tarjeta_tarifa(
            contenedor,
            1,
            "TARIFA EN MOVIMIENTO",
            self.tarifa_movimiento,
            self.VERDE,
        )

    def _crear_tarjeta_tarifa(
        self,
        parent: tk.Widget,
        columna: int,
        titulo: str,
        tarifa: float,
        color: str,
    ) -> None:
        tarjeta = tk.Frame(
            parent,
            bg=self.PANEL,
            padx=16,
            pady=10,
            highlightbackground=self.BORDE,
            highlightthickness=1,
        )
        tarjeta.grid(
            row=0,
            column=columna,
            sticky="ew",
            padx=(0, 6) if columna == 0 else (6, 0),
        )
        self._aplicar_textura_carbono(tarjeta)

        tk.Label(
            tarjeta,
            text=titulo,
            bg=self.PANEL,
            fg=self.GRIS,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w")

        tk.Label(
            tarjeta,
            text=f"{tarifa:.2f} €/segundo".replace(".", ","),
            bg=self.PANEL,
            fg=color,
            font=("Segoe UI", 15, "bold"),
        ).pack(anchor="w", pady=(3, 0))

    # ---------------------------------------------------------
    # CONTROLES
    # ---------------------------------------------------------

    def _crear_controles(self, parent: tk.Widget) -> None:
        panel = tk.Frame(
            parent,
            bg=self.PANEL,
            padx=16,
            pady=12,
            highlightbackground=self.BORDE,
            highlightthickness=1,
        )
        panel.grid(row=3, column=0, sticky="ew", pady=(0, 12))
        self._aplicar_textura_carbono(panel)
        panel.columnconfigure((0, 1, 2, 3), weight=1)

        tk.Label(
            panel,
            text="CONTROL DE CARRERA",
            bg=self.PANEL,
            fg=self.GRIS,
            font=("Segoe UI", 9, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=4,
            sticky="w",
            pady=(0, 8),
        )

        self.btn_iniciar = self._crear_boton(
            panel,
            "INICIAR",
            self._iniciar,
            self.AMARILLO,
            self.FONDO,
        )
        self.btn_iniciar.grid(row=1, column=0, sticky="ew", padx=4)

        self.btn_parado = self._crear_boton(
            panel,
            "PARADO",
            lambda: self._cambiar_estado("parado"),
            self.AMARILLO,
            self.FONDO,
        )
        self.btn_parado.grid(row=1, column=1, sticky="ew", padx=4)

        self.btn_movimiento = self._crear_boton(
            panel,
            "EN MOVIMIENTO",
            lambda: self._cambiar_estado("movimiento"),
            self.AMARILLO,
            self.FONDO,
        )
        self.btn_movimiento.grid(row=1, column=2, sticky="ew", padx=4)

        self.btn_finalizar = self._crear_boton(
            panel,
            "FINALIZAR",
            self._finalizar,
            self.AMARILLO,
            self.FONDO,
        )
        self.btn_finalizar.grid(row=1, column=3, sticky="ew", padx=4)

        self.btn_reintentar = self._crear_boton(
            panel,
            "REINTENTAR GUARDADO",
            self._reintentar_guardado,
            self.AMARILLO,
            self.FONDO,
        )
        self.btn_reintentar.grid(
            row=2,
            column=0,
            columnspan=4,
            sticky="ew",
            padx=4,
            pady=(8, 0),
        )
        # Solo se muestra cuando falla el guardado automático.
        self.btn_reintentar.grid_remove()

    def _crear_boton(
        self,
        parent: tk.Widget,
        texto: str,
        comando,
        fondo: str,
        texto_color: str,
    ) -> tk.Button:
        return tk.Button(
            parent,
            text=texto,
            command=comando,
            bg=fondo,
            fg=texto_color,
            activebackground="#FFE16A",
            activeforeground=self.FONDO,
            disabledforeground="#76652A",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            bd=0,
            padx=8,
            pady=11,
            cursor="hand2",
        )

    # ---------------------------------------------------------
    # HISTORIAL
    # ---------------------------------------------------------

    def _crear_historial(self, parent: tk.Widget) -> None:
        panel = tk.Frame(
            parent,
            bg=self.PANEL,
            padx=14,
            pady=10,
            highlightbackground=self.BORDE,
            highlightthickness=1,
        )
        panel.grid(row=4, column=0, sticky="nsew")
        self._aplicar_textura_carbono(panel)
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)

        tk.Label(
            panel,
            text="HISTORIAL DE CARRERAS",
            bg=self.PANEL,
            fg=self.BLANCO,
            font=("Segoe UI", 9, "bold"),
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 8),
        )

        tabla_contenedor = tk.Frame(panel, bg=self.PANEL)
        tabla_contenedor.grid(row=1, column=0, sticky="nsew")
        tabla_contenedor.columnconfigure(0, weight=1)
        tabla_contenedor.rowconfigure(0, weight=1)

        columnas = ("fecha", "duracion", "importe")

        self.tabla = ttk.Treeview(
            tabla_contenedor,
            columns=columnas,
            show="headings",
            height=4,
        )

        self.tabla.heading("fecha", text="FECHA")
        self.tabla.heading("duracion", text="DURACIÓN")
        self.tabla.heading("importe", text="IMPORTE")

        self.tabla.column("fecha", width=450, anchor="w")
        self.tabla.column("duracion", width=150, anchor="center")
        self.tabla.column("importe", width=150, anchor="e")

        scrollbar = ttk.Scrollbar(
            tabla_contenedor,
            orient="vertical",
            command=self.tabla.yview,
            style="Vertical.TScrollbar",
        )

        self.tabla.configure(yscrollcommand=scrollbar.set)
        self.tabla.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    # ---------------------------------------------------------
    # LÓGICA DE CARRERA
    # ---------------------------------------------------------

    def _iniciar(self) -> None:
        try:
            self.taximetro.iniciar_carrera()

            self.importe_var.set("0,00 €")
            self.duracion_var.set("00:00:00")
            self._actualizar_estado_visual()

            self._actualizar_controles()
            logger.info(
                "Nueva carrera iniciada desde la interfaz gráfica"
            )

        except RuntimeError as error:
            messagebox.showerror("No se puede iniciar", str(error))

    def _cambiar_estado(self, estado: str) -> None:
        try:
            carrera = self.taximetro.carrera_actual

            if carrera is None:
                raise RuntimeError("No hay ninguna carrera activa.")

            if carrera.estado != estado:
                self.taximetro.cambiar_estado(estado)

            self._actualizar_estado_visual()
            self._actualizar_controles()

        except (RuntimeError, ValueError) as error:
            messagebox.showerror("Error de estado", str(error))

    def _actualizar_estado_visual(self) -> None:
        texto = self._texto_estado()
        color = self._color_estado()

        self.estado_var.set(texto)
        self.etiqueta_estado.configure(fg=color)
        self._dibujar_indicador()

    def _finalizar(self) -> None:
        try:
            carrera = self.taximetro.finalizar_carrera()
            self.carrera_pendiente_guardar = carrera

            self.importe_var.set(
                f"{carrera.importe:.2f} €".replace(".", ",")
            )

            self.duracion_var.set(
                self._formatear_duracion(carrera.duracion_segundos)
            )

            self.estado_var.set("FINALIZADA")
            self.etiqueta_estado.configure(fg=self.VERDE)
            self._dibujar_indicador()

            # El guardado se intenta automáticamente al finalizar.
            self._reintentar_guardado()

        except RuntimeError as error:
            messagebox.showerror("Error", str(error))

    def _reintentar_guardado(self) -> None:
        if self.carrera_pendiente_guardar is None:
            return

        try:
            guardar_carrera(self.carrera_pendiente_guardar)

            self.carrera_pendiente_guardar = None

            self._cargar_historial()
            self._actualizar_controles()
            self._dibujar_indicador()

            messagebox.showinfo(
                "Carrera guardada",
                "La carrera se ha guardado correctamente.",
            )

        except (OSError, ValueError) as error:
            logger.exception("No se pudo guardar la carrera")

            messagebox.showerror(
                "Error de persistencia",
                f"No se pudo guardar la carrera:\n{error}",
            )
            # Si falla, se muestra el botón para permitir otro intento.
            self._actualizar_controles()

    # ---------------------------------------------------------
    # PERSISTENCIA E HISTORIAL
    # ---------------------------------------------------------

    def _cargar_historial(self) -> None:
        try:
            registros = cargar_historial()

            for elemento in self.tabla.get_children():
                self.tabla.delete(elemento)

            for registro in reversed(registros):
                importe = registro.get("importe_euros", 0)
                duracion = registro.get("duracion_segundos", 0)

                self.tabla.insert(
                    "",
                    "end",
                    values=(
                        registro.get("fecha_inicio", ""),
                        self._formatear_duracion(duracion),
                        f"{importe:.2f} €".replace(".", ","),
                    ),
                )

        except (OSError, ValueError) as error:
            logger.exception("No se pudo cargar el historial")
            messagebox.showerror("Error de historial", str(error))

    # ---------------------------------------------------------
    # RELOJ Y CONTROLES
    # ---------------------------------------------------------

    def _actualizar_reloj(self) -> None:
        carrera = self.taximetro.carrera_actual

        if carrera is not None:
            carrera.actualizar()

            self.importe_var.set(
                f"{carrera.importe:.2f} €".replace(".", ",")
            )

            duracion = monotonic() - carrera.inicio
            self.duracion_var.set(
                self._formatear_duracion(duracion)
            )

            if carrera.estado == "movimiento":
                self.tarifa_activa_var.set(
                    f"Movimiento · {self.tarifa_movimiento:.2f} €/segundo".replace(".", ",", 1)
                )
            else:
                self.tarifa_activa_var.set(
                    f"Parado · {self.tarifa_parado:.2f} €/segundo".replace(".", ",", 1)
                )
        else:
            self.tarifa_activa_var.set("A la espera de carrera")

        self.root.after(250, self._actualizar_reloj)

    @staticmethod
    def _formatear_duracion(segundos: float) -> str:
        total = max(0, int(segundos))
        horas, resto = divmod(total, 3600)
        minutos, segundos = divmod(resto, 60)

        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

    def _actualizar_controles(self) -> None:
        activa = self.taximetro.hay_carrera_activa()
        pendiente = self.carrera_pendiente_guardar is not None

        self.btn_iniciar.configure(
            state="disabled" if activa or pendiente else "normal"
        )

        self.btn_finalizar.configure(
            state="normal" if activa else "disabled"
        )

        self.btn_parado.configure(
            state="normal" if activa else "disabled"
        )

        self.btn_movimiento.configure(
            state="normal" if activa else "disabled"
        )

        self.btn_reintentar.configure(
            state="normal" if pendiente else "disabled"
        )

        # El botón solo ocupa espacio cuando hay un guardado pendiente.
        if pendiente:
            self.btn_reintentar.grid()
        else:
            self.btn_reintentar.grid_remove()

    # ---------------------------------------------------------
    # CIERRE SEGURO
    # ---------------------------------------------------------

    def _cerrar(self) -> None:
        if self.taximetro.hay_carrera_activa():
            messagebox.showwarning(
                "Carrera activa",
                "Debes finalizar la carrera antes de cerrar la aplicación.",
            )
            return

        if self.carrera_pendiente_guardar is not None:
            messagebox.showwarning(
                "Guardado pendiente",
                "Debes guardar la última carrera antes de cerrar.",
            )
            return

        self.root.destroy()


def ejecutar_grafica() -> None:
    """Punto de entrada de la interfaz gráfica."""

    # Comprobar el acceso antes de abrir la ventana principal.
    if not autenticar_grafica():
        return

    configurar_logging()

    root = tk.Tk()
    VentanaTaximetro(root)
    root.mainloop()


if __name__ == "__main__":
    ejecutar_grafica()
