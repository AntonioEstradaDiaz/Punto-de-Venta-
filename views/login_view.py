# views/login_view.py

import flet as ft
from flet.controls.material.icons import Icons

# ─────────────────────────────────────────────────────────────────
# CREDENCIALES (cámbialas aquí si quieres)
# ─────────────────────────────────────────────────────────────────
USUARIOS = {
    "admin": {"password": "admin123", "rol": "admin"},
    "user":  {"password": "user123",  "rol": "user"},
}


class LoginView(ft.Container):
    """
    Pantalla de inicio de sesión.

    Al autenticarse correctamente llama a on_login(rol: str)
    para que main.py sepa qué rol tiene el usuario y construya
    el sidebar adecuado.
    """

    def __init__(self, page: ft.Page, on_login):
        super().__init__(expand=True, bgcolor="#0f172a")
        self.main_page = page
        self.on_login  = on_login

        # Controles del formulario
        self._campo_usuario = ft.TextField(
            label="Usuario",
            prefix_icon=Icons.PERSON,
            border_color="#38bdf8",
            focused_border_color="#38bdf8",
            width=340,
            text_size=16,
        )
        self._campo_password = ft.TextField(
            label="Contraseña",
            prefix_icon=Icons.LOCK,
            password=True,
            can_reveal_password=True,
            border_color="#38bdf8",
            focused_border_color="#38bdf8",
            width=340,
            text_size=16,
            on_submit=self._intentar_login,   # Enter también funciona
        )
        self._txt_error = ft.Text(
            "",
            color="#ef4444",
            size=13,
            visible=False,
        )

        self.content = self._build_ui()

    # ── UI ────────────────────────────────────────────────────────
    def _build_ui(self):
        tarjeta = ft.Container(
            bgcolor="#1e293b",
            border_radius=16,
            padding=40,
            width=420,
            content=ft.Column(
                [
                    # Logo / título
                    ft.Row(
                        [
                            ft.Icon(Icons.RESTAURANT, color="#38bdf8", size=36),
                            ft.Text(
                                "SaaS POS",
                                size=30,
                                weight="bold",
                                color="white",
                            ),
                        ],
                        alignment="center",
                        spacing=10,
                    ),
                    ft.Text(
                        "Sistema de Punto de Venta",
                        size=13,
                        color="#64748b",
                        text_align="center",
                    ),
                    ft.Container(height=28),
                    # Campos
                    self._campo_usuario,
                    ft.Container(height=12),
                    self._campo_password,
                    ft.Container(height=6),
                    self._txt_error,
                    ft.Container(height=18),
                    # Botón
                    ft.ElevatedButton(
                        "INICIAR SESIÓN",
                        icon=Icons.LOGIN,
                        on_click=self._intentar_login,
                        bgcolor="#38bdf8",
                        color="#0f172a",
                        height=52,
                        width=340,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10)
                        ),
                    ),
                    ft.Container(height=20),
                    # Pista de credenciales (quítala en producción)
                    ft.Container(
                        bgcolor="#0f172a",
                        border_radius=8,
                        padding=12,
                        content=ft.Column(
                            [
                                ft.Text(
                                    "Credenciales de prueba:",
                                    size=11,
                                    color="#475569",
                                    weight="bold",
                                ),
                                ft.Text(
                                    "Admin → usuario: admin  |  contraseña: admin123",
                                    size=11,
                                    color="#475569",
                                ),
                                ft.Text(
                                    "User  → usuario: user   |  contraseña: user123",
                                    size=11,
                                    color="#475569",
                                ),
                            ],
                            spacing=2,
                        ),
                    ),
                ],
                horizontal_alignment="center",
                spacing=0,
            ),
        )

        return ft.Column(
            [tarjeta],
            alignment="center",
            horizontal_alignment="center",
            expand=True,
        )

    # ── Lógica ────────────────────────────────────────────────────
    def _intentar_login(self, e):
        usuario  = self._campo_usuario.value.strip().lower()
        password = self._campo_password.value

        info = USUARIOS.get(usuario)

        if info and info["password"] == password:
            self._txt_error.visible = False
            self._txt_error.update()
            self.on_login(info["rol"])          # ← notifica a main
        else:
            self._txt_error.value   = "Usuario o contraseña incorrectos."
            self._txt_error.visible = True
            self._campo_password.value = ""
            self.main_page.update()
