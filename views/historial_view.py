import flet as ft
from flet.controls.material.icons import Icons


class HistorialView(ft.Container):
    def __init__(self, page, data_manager):
        super().__init__(expand=True, padding=30)
        self.main_page = page
        self.dm = data_manager
        self.lista = ft.ListView(expand=True, spacing=6)
        self.content = self._build_ui()

    def did_mount(self):
        self._cargar_historial()

    def _build_ui(self):
        return ft.Column([
            ft.Row([
                ft.Icon(Icons.HISTORY, color="#38bdf8", size=30),
                ft.Text("Historial de Ventas – Hoy", size=26, weight="bold", color="#38bdf8"),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=Icons.REFRESH,
                    icon_color="#38bdf8",
                    tooltip="Actualizar",
                    on_click=lambda e: self._cargar_historial()
                )
            ], vertical_alignment="center"),
            ft.Container(height=10),
            ft.Container(
                expand=True,
                bgcolor="#1e293b",
                border_radius=12,
                padding=20,
                content=ft.Column([
                    ft.Row([
                        ft.Container(ft.Text("HORA",  size=13, weight="bold", color="#64748b"), width=80),
                        ft.Container(ft.Text("PRODUCTOS", size=13, weight="bold", color="#64748b"), expand=True),
                        ft.Text("TOTAL", size=13, weight="bold", color="#64748b"),
                    ]),
                    ft.Divider(color="#334155"),
                    self.lista,
                ], expand=True)
            ),
        ], expand=True)

    def _cargar_historial(self):
        self.lista.controls.clear()
        ventas = self.dm.get_historial_hoy()

        if not ventas:
            self.lista.controls.append(
                ft.Container(
                    ft.Text("Sin ventas registradas hoy.", color="#64748b", size=15),
                    padding=ft.padding.only(top=20)
                )
            )
        else:
            for i, v in enumerate(reversed(ventas), 1):
                hora = v.get("hora", "--:--")
                total = v.get("total", 0)
                productos = v.get("productos", {})
                detalle = ", ".join(f"{c}x {p}" for p, c in productos.items())

                self.lista.controls.append(
                    ft.Container(
                        bgcolor="#0f172a" if i % 2 == 0 else "#1e293b",
                        border_radius=8,
                        padding=ft.padding.symmetric(horizontal=10, vertical=8),
                        content=ft.Row([
                            ft.Container(
                                ft.Text(hora, size=14, color="#38bdf8", weight="bold"),
                                width=80
                            ),
                            ft.Text(
                                detalle if detalle else "—",
                                size=13,
                                color="#cbd5e1",
                                expand=True,
                                no_wrap=False,
                            ),
                            ft.Text(
                                f"${total:.2f}",
                                size=15,
                                weight="bold",
                                color="white"
                            ),
                        ], vertical_alignment="center")
                    )
                )
def _abrir_modal_grafica(self, e):
        # 1. OBTENER LAS VENTAS REALES DEL DÍA EN TIEMPO REAL
        ventas_hoy = self.dm.get_historial_hoy() or []
        
        # 2. CALCULAR LA SUMA TOTAL DE LAS VENTAS DE HOY
        total_hoy = sum(v.get("total", 0.0) for v in ventas_hoy)

        # 3. CONSTRUIRE EL HISTORIAL DE PERIODOS 
       
        datos_periodos = [
            {"periodo": "Hoy", "ganancia": total_hoy},       
            {"periodo": "Semana", "ganancia": total_hoy * 1.5},    
            {"periodo": "Año", "ganancia": total_hoy * 2.2},    
        ]

        filas_grafica = []
        # Si no hay ventas, definimos el máximo como 1.0 para evitar divisiones entre cero
        max_ganancia = max(d["ganancia"] for d in datos_periodos) if any(d["ganancia"] > 0 for d in datos_periodos) else 1.0

        for dato in datos_periodos:
            ganancia = dato["ganancia"]
            color_barra, etiqueta = self._obtener_estilo_barra(ganancia)
            
            # Ancho fijo proporcional adaptivo: si la ganancia es 0, la barra mide el mínimo (30px)
            ancho_barra = int((ganancia / max_ganancia) * 220) + 30 if ganancia > 0 else 30
        self.lista.update()
