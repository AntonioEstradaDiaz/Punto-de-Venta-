# views/reporte_general_view.py

import flet as ft
from flet.controls.material.icons import Icons


class ReporteGeneralView(ft.Container):
    """
    Muestra el historial acumulado de TODOS los cierres de día:
      - KPIs globales: total ventas, total gastos, ganancia neta, nº de días
      - Tabla de cierres (fecha, ventas, gastos, ganancia)
      - Gráfica de barras de ganancias por fecha
    Solo requiere el método get_reporte_general() en DataManager.
    """

    def __init__(self, page: ft.Page, data_manager):
        super().__init__(expand=True, padding=30, bgcolor="#0f172a")
        self.main_page = page
        self.dm        = data_manager
        self.content   = self._build_ui()

    # ── construcción ──────────────────────────────────────────────
    def _build_ui(self):
        data = self.dm.get_reporte_general()

        encabezado = ft.Row(
            [
                ft.Icon(Icons.ASSESSMENT, color="#a78bfa", size=30),
                ft.Text(
                    "Reporte General Histórico",
                    size=26,
                    weight="bold",
                    color="#a78bfa",
                ),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=Icons.REFRESH,
                    icon_color="#a78bfa",
                    tooltip="Actualizar",
                    on_click=lambda e: self._refrescar(),
                ),
            ],
            vertical_alignment="center",
        )

        # ── KPI Cards ─────────────────────────────────────────────
        kpis = ft.Row(
            [
                self._kpi("Total Ventas",   f"${data['total_ventas']:.2f}",   Icons.TRENDING_UP,            "#4ade80"),
                self._kpi("Total Gastos",   f"${data['total_gastos']:.2f}",   Icons.TRENDING_DOWN,           "#f87171"),
                self._kpi("Ganancia Neta",  f"${data['ganancia_neta']:.2f}",  Icons.ACCOUNT_BALANCE_WALLET,  "#38bdf8"),
                self._kpi("Días Cerrados",  str(data["num_dias"]),             Icons.CALENDAR_TODAY,          "#f59e0b"),
            ],
            alignment="spaceEvenly",
        )

        # ── Gráfica de barras ──────────────────────────────────────
        panel_grafica = self._grafica_barras(data["cierres"])

        # ── Tabla de cierres ───────────────────────────────────────
        panel_tabla = self._tabla_cierres(data["cierres"])

        return ft.Column(
            [
                encabezado,
                ft.Container(height=16),
                kpis,
                ft.Container(height=20),
                ft.Row(
                    [panel_grafica, ft.Container(width=16), panel_tabla],
                    expand=True,
                    vertical_alignment="start",
                ),
            ],
            expand=True,
        )

    # ── helpers de UI ─────────────────────────────────────────────
    def _kpi(self, titulo, valor, icono, color):
        return ft.Container(
            expand=1,
            bgcolor="#1e293b",
            border_radius=12,
            padding=20,
            content=ft.Row(
                [
                    ft.Icon(icono, size=36, color=color),
                    ft.Column(
                        [
                            ft.Text(titulo, size=13, color="#64748b"),
                            ft.Text(valor,  size=22, weight="bold", color="white"),
                        ],
                        spacing=2,
                    ),
                ],
                alignment="center",
            ),
        )

    def _grafica_barras(self, cierres: list):
        """Barras verticales de ganancia por fecha (mismo estilo que DashboardView)."""
        if not cierres:
            return ft.Container(
                expand=1,
                bgcolor="#1e293b",
                border_radius=12,
                padding=20,
                content=ft.Text("Sin cierres registrados.", color="#64748b"),
            )

        # Tomar máximo para escalar; separar positivos y negativos visualmente
        max_abs = max(abs(c["ganancia"]) for c in cierres) or 1
        chart_h  = 160

        def color_barra(g):
            return "#4ade80" if g >= 0 else "#f87171"

        barras = ft.Row(
            spacing=0,
            expand=True,
            alignment="spaceAround",
            vertical_alignment="end",
            controls=[
                ft.Column(
                    [
                        ft.Text(
                            f"${c['ganancia']:.0f}",
                            size=9,
                            color=color_barra(c["ganancia"]),
                            text_align="center",
                        ),
                        ft.Container(
                            width=28,
                            height=max(4, int((abs(c["ganancia"]) / max_abs) * chart_h)),
                            bgcolor=color_barra(c["ganancia"]),
                            border_radius=ft.BorderRadius(
                                top_left=4, top_right=4,
                                bottom_left=0, bottom_right=0,
                            ),
                        ),
                        ft.Text(
                            c["fecha"],
                            size=8,
                            color="grey",
                            text_align="center",
                        ),
                    ],
                    horizontal_alignment="center",
                    spacing=4,
                )
                for c in cierres[-20:]   # mostramos máximo los últimos 20 días
            ],
        )

        return ft.Container(
            expand=1,
            bgcolor="#1e293b",
            border_radius=12,
            padding=20,
            content=ft.Column(
                [
                    ft.Text(
                        "Ganancia por Día",
                        size=16,
                        weight="bold",
                        color="white",
                    ),
                    ft.Text(
                        "Verde = ganancia  |  Rojo = pérdida",
                        size=11,
                        color="#64748b",
                    ),
                    ft.Divider(color="#334155"),
                    ft.Container(
                        content=barras,
                        height=chart_h + 40,
                    ),
                ]
            ),
        )

    def _tabla_cierres(self, cierres: list):
        """Tabla con todos los cierres en orden cronológico inverso."""
        encabezado_fila = ft.Row(
            [
                ft.Container(ft.Text("FECHA",    size=12, weight="bold", color="#64748b"), width=90),
                ft.Container(ft.Text("VENTAS",   size=12, weight="bold", color="#64748b"), width=90),
                ft.Container(ft.Text("GASTOS",   size=12, weight="bold", color="#64748b"), width=90),
                ft.Text("GANANCIA", size=12, weight="bold", color="#64748b"),
            ]
        )

        filas = []
        for i, c in enumerate(reversed(cierres)):
            color_gan = "#4ade80" if c["ganancia"] >= 0 else "#f87171"
            bg        = "#0f172a" if i % 2 == 0 else "#1e293b"
            filas.append(
                ft.Container(
                    bgcolor=bg,
                    border_radius=6,
                    padding=ft.padding.symmetric(horizontal=8, vertical=7),
                    content=ft.Row(
                        [
                            ft.Container(
                                ft.Text(c["fecha"], size=13, color="#cbd5e1"),
                                width=90,
                            ),
                            ft.Container(
                                ft.Text(f"${c['ventas']:.2f}", size=13, color="#4ade80"),
                                width=90,
                            ),
                            ft.Container(
                                ft.Text(f"${c['gastos']:.2f}", size=13, color="#f87171"),
                                width=90,
                            ),
                            ft.Text(
                                f"${c['ganancia']:.2f}",
                                size=13,
                                weight="bold",
                                color=color_gan,
                            ),
                        ]
                    ),
                )
            )

        if not filas:
            filas.append(
                ft.Container(
                    ft.Text("Sin cierres registrados aún.", color="#64748b", size=14),
                    padding=ft.padding.only(top=16),
                )
            )

        lista = ft.ListView(
            controls=filas,
            expand=True,
            spacing=3,
        )

        return ft.Container(
            expand=1,
            bgcolor="#1e293b",
            border_radius=12,
            padding=20,
            content=ft.Column(
                [
                    ft.Text("Detalle de Cierres", size=16, weight="bold", color="white"),
                    ft.Divider(color="#334155"),
                    encabezado_fila,
                    ft.Divider(color="#334155", height=1),
                    lista,
                ],
                expand=True,
            ),
        )

    # ── refresco ──────────────────────────────────────────────────
    def _refrescar(self):
        self.content = self._build_ui()
        try:
            self.update()
        except RuntimeError:
            pass
