# main.py  (versión con Login + Roles)

import flet as ft
from flet.controls.material.icons import Icons

from core.data_manager import DataManager
from views.login_view import LoginView
from views.pos_view import POSView
from views.gastos_view import GastosView
from views.dashboard_view import DashboardView
from views.historial_view import HistorialView
from views.cierre_dia_view import CierreDiaView
from views.reporte_general_view import ReporteGeneralView


# ─────────────────────────────────────────────────────────────────
# Definición de destinos por rol
# ─────────────────────────────────────────────────────────────────

def _get_destinos(rol: str):
    """
    Retorna la lista de (label, icono, view_class) permitidos según el rol.
    admin → todo
    user  → solo Ventas e Historial
    """
    todos = [
        ("Ventas",          Icons.SHOPPING_CART,        POSView),
        ("Gastos",          Icons.PAYMENT,               GastosView),
        ("Dashboard",       Icons.ANALYTICS,             DashboardView),
        ("Historial",       Icons.HISTORY,               HistorialView),
        ("Cerrar Día",      Icons.NIGHTLIGHT,            CierreDiaView),
        ("Reporte General", Icons.ASSESSMENT,            ReporteGeneralView),
    ]
    if rol == "admin":
        return todos
    # rol == "user": solo ventas e historial
    permitidos = {"Ventas", "Historial"}
    return [d for d in todos if d[0] in permitidos]


# ─────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────

def main(page: ft.Page):
    try:
        page.title      = "SaaS POS System"
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor    = "#0f172a"
        page.padding    = 0

        dm = DataManager()

        # ── Pantalla principal (sidebar + contenido) ───────────────
        def mostrar_app(rol: str):
            """Se llama desde LoginView cuando el usuario se autentica."""
            page.controls.clear()

            destinos = _get_destinos(rol)
            content_area = ft.Container(expand=True, bgcolor="#0f172a")

            def change_route(e):
                idx = e.control.selected_index
                content_area.content = None
                view_class = destinos[idx][2]
                content_area.content = view_class(page, dm)
                page.update()

            def cerrar_sesion(e):
                """Vuelve a la pantalla de login."""
                page.controls.clear()
                page.add(LoginView(page, on_login=mostrar_app))
                page.update()

            # Construir los NavigationRailDestination dinámicamente
            rail_destinations = [
                ft.NavigationRailDestination(icon=icono, label=label)
                for label, icono, _ in destinos
            ]

            # Indicador de rol (esquina superior del sidebar)
            etiqueta_rol = ft.Container(
                bgcolor="#0f172a",
                border_radius=8,
                padding=ft.padding.symmetric(horizontal=10, vertical=4),
                margin=ft.margin.only(bottom=8),
                content=ft.Text(
                    f"👤 {rol.upper()}",
                    size=11,
                    color="#38bdf8" if rol == "admin" else "#94a3b8",
                    weight="bold",
                ),
            )

            sidebar = ft.NavigationRail(
                selected_index=0,
                label_type=ft.NavigationRailLabelType.ALL,
                min_width=100,
                min_extended_width=200,
                bgcolor="#1e293b",
                on_change=change_route,
                destinations=rail_destinations,
                leading=etiqueta_rol,
                trailing=ft.IconButton(
                    icon=Icons.LOGOUT,
                    icon_color="#ef4444",
                    tooltip="Cerrar sesión",
                    on_click=cerrar_sesion,
                ),
            )

            # Vista inicial = primera de la lista permitida
            content_area.content = destinos[0][2](page, dm)

            page.add(
                ft.Row(
                    [
                        sidebar,
                        ft.VerticalDivider(width=1, color="#334155"),
                        content_area,
                    ],
                    expand=True,
                )
            )
            page.update()

        # ── Arrancar con el Login ──────────────────────────────────
        page.add(LoginView(page, on_login=mostrar_app))
        page.update()

    except Exception as ex:
        import traceback
        page.bgcolor = "#0f172a"
        page.add(
            ft.Column(
                [
                    ft.Text("❌ ERROR AL INICIAR", size=20, weight="bold", color="red"),
                    ft.Text(str(ex), color="orange", selectable=True),
                    ft.Text(traceback.format_exc(), size=11, color="#aaaaaa", selectable=True),
                ],
                scroll="auto",
            )
        )
        page.update()


if __name__ == "__main__":
    ft.run(main)
