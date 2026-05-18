import flet as ft
from flet.controls.material.icons import Icons
from datetime import datetime

class CierreDiaView(ft.Container):
    def __init__(self, page, data_manager):
        super().__init__(expand=True, padding=30)
        self.main_page = page
        self.dm = data_manager
        
        # Filtro activo por defecto
        self.filtro_activo = "hoy"
        self.fecha_buscada = datetime.now()
        
        # --- Elementos Reactivos de la UI ---
        self._txt_reporte = ft.Text("Mostrando: Datos de Hoy", size=14, color="#64748b", weight="bold")
        self._txt_estado = ft.Text("", size=14, color="#38bdf8")
        
        # Gráficas de Contenedores
        self.chart_h = 140
        self.txt_v = ft.Text("$0.00", size=11, color="#4ade80", weight="bold")
        self.txt_g = ft.Text("$0.00", size=11, color="#f87171", weight="bold")
        self.txt_gan = ft.Text("$0.00", size=11, color="#38bdf8", weight="bold")
        
        self.barra_ventas = ft.Container(width=50, height=4, bgcolor="#4ade80", border_radius=ft.BorderRadius(6,6,0,0))
        self.barra_gastos = ft.Container(width=50, height=4, bgcolor="#f87171", border_radius=ft.BorderRadius(6,6,0,0))
        self.barra_ganancia = ft.Container(width=50, height=4, bgcolor="#38bdf8", border_radius=ft.BorderRadius(6,6,0,0))
        
        # Tarjetas KPI superiores
        self.card_ventas_val = ft.Text("$0.00", size=26, weight="bold", color="white")
        self.card_gastos_val = ft.Text("$0.00", size=26, weight="bold", color="white")
        self.card_ganancia_val = ft.Text("$0.00", size=26, weight="bold", color="white")
        
        self.content = self._build_ui()

    def procesar_y_actualizar(self, tipo_filtro, fecha_esp=None):
        """
        Calcula de forma dinámica las sumas acumuladas de ventas, gastos y ganancias
        según el botón presionado o la fecha seleccionada en el calendario.
        """
        ventas, gastos, ganancia = 0.0, 0.0, 0.0
        hoy = datetime.now()
        self.filtro_activo = tipo_filtro
        
        # 1. CASO HOY: Trae los KPIs en tiempo real de la sesión actual
        if tipo_filtro == "hoy":
            data = self.dm.get_kpis_y_graficos()
            ventas = float(data.get('ventas_hoy', 0))
            gastos = float(data.get('gastos_hoy', 0))
            ganancia = float(data.get('ganancia', 0))
            self._txt_reporte.value = "Mostrando: Datos de Hoy"
            
        else:
            # Obtener el historial completo desde el data_manager
            historico = []
            if hasattr(self.dm, 'get_todo_el_historico'):
                historico = self.dm.get_todo_el_historico()
            
            if not historico:
                historico = []

            # 2. PROCESAR HISTORIAL CON FILTROS DINÁMICOS
            for registro in historico:
                try:
                    fecha_str = registro.get('fecha', '')
                    if "-" in fecha_str:
                        reg_date = datetime.strptime(fecha_str.split()[0], "%Y-%m-%d")
                    else:
                        reg_date = datetime.strptime(fecha_str.split()[0], "%d/%m/%Y")
                except Exception:
                    continue  # Si hay error en formato, salta el registro
                
                v_reg = float(registro.get('ventas', 0) or 0)
                g_reg = float(registro.get('gastos', 0) or 0)
                gan_reg = float(registro.get('ganancia', 0) or 0)

                if tipo_filtro == "busqueda" and fecha_esp:
                    if reg_date.date() == fecha_esp.date():
                        ventas += v_reg
                        gastos += g_reg
                        ganancia += gan_reg

                elif tipo_filtro == "semana":
                    if (hoy - reg_date).days <= 7 and reg_date <= hoy:
                        ventas += v_reg
                        gastos += g_reg
                        ganancia += gan_reg
                        
                elif tipo_filtro == "mes":
                    if reg_date.month == hoy.month and reg_date.year == hoy.year:
                        ventas += v_reg
                        gastos += g_reg
                        ganancia += gan_reg
                        
                elif tipo_filtro == "ano":
                    if reg_date.year == hoy.year:
                        ventas += v_reg
                        gastos += g_reg
                        ganancia += gan_reg

            if tipo_filtro == "busqueda" and fecha_esp:
                self._txt_reporte.value = f"Mostrando Día Específico: {fecha_esp.strftime('%d/%m/%Y')}"
            else:
                self._txt_reporte.value = f"Mostrando Acumulado: Este {tipo_filtro.capitalize() if tipo_filtro != 'ano' else 'Año'}"

        # --- RE-RENDERIZAR VALORES EN LA INTERFAZ ---
        self.card_ventas_val.value = f"${ventas:,.2f}"
        self.card_gastos_val.value = f"${gastos:,.2f}"
        self.card_ganancia_val.value = f"${ganancia:,.2f}"
        
        self.txt_v.value = f"${ventas:,.2f}"
        self.txt_g.value = f"${gastos:,.2f}"
        self.txt_gan.value = f"${ganancia:,.2f}"
        
        max_valor = max(ventas, gastos, abs(ganancia), 1.0)
        
        self.barra_ventas.height = max(4, int((ventas / max_valor) * self.chart_h))
        self.barra_gastos.height = max(4, int((gastos / max_valor) * self.chart_h))
        
        if ganancia >= 0:
            self.barra_ganancia.bgcolor = "#38bdf8"
            self.barra_ganancia.height = max(4, int((ganancia / max_valor) * self.chart_h))
        else:
            self.barra_ganancia.bgcolor = "#f43f5e"
            self.barra_ganancia.height = max(4, int((abs(ganancia) / max_valor) * self.chart_h))
        
        self.main_page.update()

    def _build_ui(self):
        def fecha_buscada_cambiada(e):
            if date_picker.value:
                self.fecha_buscada = date_picker.value
                self.procesar_y_actualizar("busqueda", self.fecha_buscada)

        date_picker = ft.DatePicker(
            on_change=fecha_buscada_cambiada,
            first_date=datetime(2025, 1, 1),
            last_date=datetime(2030, 12, 31)
        )
        self.main_page.overlay.append(date_picker)

        def cambio_filtro(e):
            boton_pulsado = e.control.data
            self.procesar_y_actualizar(boton_pulsado)

        def hacer_cierre(e):
            resumen, ruta = self.dm.cerrar_dia()
            self._txt_estado.value = f"✅ Cierre guardado en:\n{ruta}"
            self._txt_estado.color = "#4ade80"
            
            self.procesar_y_actualizar(self.filtro_activo)
            
            snack = ft.SnackBar(ft.Text("✅ Cierre del día guardado correctamente"), bgcolor="#166534")
            self.main_page.overlay.append(snack)
            snack.open = True
            self.main_page.update()

        def abrir_calendario(e):
            date_picker.open = True
            self.main_page.update()

        botones_tiempo = ft.Row([
            ft.TextButton("Hoy", data="hoy", on_click=cambio_filtro, style=ft.ButtonStyle(color="white")),
            ft.TextButton("Esta Semana", data="semana", on_click=cambio_filtro, style=ft.ButtonStyle(color="white")),
            ft.TextButton("Este Mes", data="mes", on_click=cambio_filtro, style=ft.ButtonStyle(color="white")),
            ft.TextButton("Este Año", data="ano", on_click=cambio_filtro, style=ft.ButtonStyle(color="white")),
        ], spacing=10)

        grafico_balance = ft.Row(
            spacing=30, alignment="center", vertical_alignment="end",
            controls=[
                ft.Column([self.txt_v, self.barra_ventas, ft.Text("Ventas", size=12, color="#94a3b8")], horizontal_alignment="center", spacing=4),
                ft.Column([self.txt_g, self.barra_gastos, ft.Text("Gastos", size=12, color="#94a3b8")], horizontal_alignment="center", spacing=4),
                ft.Column([self.txt_gan, self.barra_ganancia, ft.Text("Ganancia", size=12, color="#94a3b8")], horizontal_alignment="center", spacing=4),
            ]
        )

        panel_grafico = ft.Container(
            bgcolor="#0f172a", padding=20, border_radius=10,
            content=ft.Column([
                ft.Text("Análisis de Rendimiento Acumulado", size=16, weight="bold", color="white"),
                ft.Divider(color="#334155"),
                ft.Container(height=10),
                ft.Container(content=grafico_balance, height=self.chart_h + 40),
            ], horizontal_alignment="center")
        )

        self.procesar_y_actualizar("hoy")

        # 🛠️ CAMBIO CLAVE: Agregamos scroll=ft.ScrollMode.AUTO a la columna principal
        return ft.Column([
            ft.Row([
                ft.Row([
                    ft.Icon(Icons.NIGHTLIGHT, color="#f59e0b", size=30),
                    ft.Text("Cerrar Día", size=26, weight="bold", color="#f59e0b"),
                ], vertical_alignment="center"),
                
                ft.Row([
                    botones_tiempo,
                    ft.VerticalDivider(color="#334155", width=20),
                    ft.IconButton(
                        icon=Icons.SEARCH,
                        icon_color="#38bdf8",
                        tooltip="Buscar un día específico en la BD",
                        on_click=abrir_calendario
                    )
                ], vertical_alignment="center")
            ], alignment="spaceBetween", vertical_alignment="center"),
            
            self._txt_reporte,
            ft.Container(height=20),

            ft.Row([
                self._card("Ventas Totales",  self.card_ventas_val,   Icons.TRENDING_UP,          "#4ade80"),
                self._card("Gastos Totales",  self.card_gastos_val,   Icons.TRENDING_DOWN,         "#f87171"),
                self._card("Ganancia Neta",   self.card_ganancia_val, Icons.ACCOUNT_BALANCE_WALLET, "#38bdf8"),
            ], alignment="spaceEvenly"),

            ft.Container(height=30),

            ft.Container(
                bgcolor="#1e293b",
                border_radius=12,
                padding=30,
                content=ft.Column([
                    ft.Text(
                        "Al presionar el botón se guardará el resumen del día como archivo JSON y registro en BD.",
                        size=14,
                        color="#94a3b8",
                    ),
                    ft.Container(height=16),
                    ft.ElevatedButton(
                        "🌙   Cerrar Día",
                        on_click=hacer_cierre,
                        bgcolor="#f59e0b",
                        color="#0f172a",
                        height=55,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
                    ),
                    ft.Container(height=12),
                    self._txt_estado,
                    ft.Container(height=10),
                    ft.Text(
                        "El archivo se guarda en: data/cierres/YYYY-MM-DD.json",
                        size=12, color="#475569", italic=True
                    ),
                    
                    ft.Container(height=20),
                    panel_grafico
                    
                ], horizontal_alignment="start")
            ),
        ], expand=True, scroll=ft.ScrollMode.AUTO) # <-- Esto habilita el scroll suave cuando los elementos superen la pantalla

    def _card(self, titulo, control_valor, icono, color):
        return ft.Container(
            expand=1,
            bgcolor="#1e293b",
            border_radius=12,
            padding=20,
            content=ft.Row([
                ft.Icon(icono, size=38, color=color),
                ft.Column([
                    ft.Text(titulo, size=13, color="#64748b"),
                    control_valor,
                ], spacing=2)
            ], alignment="center")
        )