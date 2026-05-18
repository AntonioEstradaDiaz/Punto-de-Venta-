import flet as ft
from flet.controls.material.icons import Icons


class AddProductDialog(ft.AlertDialog):
    """
    Dialogo modal para agregar un nuevo platillo al sistema.
    """

    def __init__(self, page, data_manager, on_success):
        super().__init__()

        self.main_page = page
        self.dm = data_manager
        self.on_success = on_success

        self.txt_nombre = ft.TextField(
            label="Nombre del Platillo",
            width=300
        )

        self.txt_precio = ft.TextField(
            label="Precio",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        self.title = ft.Text(
            "Agregar Nuevo Platillo",
            weight="bold"
        )

        self.content = ft.Column([
            self.txt_nombre,
            self.txt_precio
        ], tight=True)

        self.actions = [
            ft.TextButton(
                "Cancelar",
                on_click=self._cancelar
            ),

            ft.ElevatedButton(
                "Guardar",
                on_click=self._guardar,
                bgcolor="#38bdf8",
                color="#0f172a"
            )
        ]

        self.actions_alignment = ft.MainAxisAlignment.END

    def _cancelar(self, e):
        self.open = False
        self.main_page.update()

    def _guardar(self, e):

        nombre = self.txt_nombre.value.strip()
        precio_str = self.txt_precio.value.strip()

        if not nombre or not precio_str:
            self._mostrar_snackbar(
                "⚠ Llena todos los campos",
                "#92400e"
            )
            return

        try:
            precio = float(precio_str)

        except ValueError:
            self._mostrar_snackbar(
                "⚠ El precio debe ser un numero valido",
                "#92400e"
            )
            return

        agregado = self.dm.agregar_producto(nombre, precio)

        if agregado:

            self.open = False

            self.txt_nombre.value = ""
            self.txt_precio.value = ""

            self._mostrar_snackbar(
                f"✅ Platillo '{nombre}' agregado exitosamente.",
                "#166534"
            )

            self.on_success()

        else:
            self._mostrar_snackbar(
                "⚠ El platillo ya existe",
                "#92400e"
            )

        self.main_page.update()

    def _mostrar_snackbar(self, texto, color):

        snack = ft.SnackBar(
            ft.Text(texto),
            bgcolor=color
        )

        self.main_page.overlay.append(snack)

        snack.open = True

        self.main_page.update()


class AddDiscountDialog(ft.AlertDialog):
    """
    Dialogo para agregar descuentos.
    """

    def __init__(self, page, on_success):
        super().__init__()

        self.main_page = page
        self.on_success = on_success

        self.txt_nombre = ft.TextField(
            label="Nombre del descuento",
            width=300
        )

        self.txt_monto = ft.TextField(
            label="Monto a descontar",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        self.title = ft.Text(
            "Agregar Descuento",
            weight="bold"
        )

        self.content = ft.Column([
            self.txt_nombre,
            self.txt_monto
        ], tight=True)

        self.actions = [

            ft.TextButton(
                "Cancelar",
                on_click=self._cancelar
            ),

            ft.ElevatedButton(
                "Aplicar",
                on_click=self._guardar,
                bgcolor="#f87171",
                color="white"
            )
        ]

        self.actions_alignment = ft.MainAxisAlignment.END

    def _cancelar(self, e):
        self.open = False
        self.main_page.update()

    def _guardar(self, e):

        nombre = self.txt_nombre.value.strip()
        monto_str = self.txt_monto.value.strip()

        if not nombre or not monto_str:
            self._mostrar_snackbar(
                "⚠ Llena todos los campos",
                "#92400e"
            )
            return

        try:
            monto = float(monto_str)

        except ValueError:
            self._mostrar_snackbar(
                "⚠ El monto debe ser un numero valido",
                "#92400e"
            )
            return

        self.open = False

        self.txt_nombre.value = ""
        self.txt_monto.value = ""

        self.on_success(nombre, monto)

        self._mostrar_snackbar(
            f"✅ Descuento '{nombre}' agregado",
            "#166534"
        )

        self.main_page.update()

    def _mostrar_snackbar(self, texto, color):

        snack = ft.SnackBar(
            ft.Text(texto),
            bgcolor=color
        )

        self.main_page.overlay.append(snack)

        snack.open = True

        self.main_page.update()


class DeleteProductDialog(ft.AlertDialog):

    def __init__(self, page, data_manager, on_success):
        super().__init__()

        self.main_page = page
        self.dm = data_manager
        self.on_success = on_success

        self.producto_a_eliminar = None

        self.title = ft.Text(
            "Eliminar Platillo?",
            weight="bold"
        )

        self.txt_mensaje = ft.Text("")

        self.content = self.txt_mensaje

        self.actions = [

            ft.TextButton(
                "Cancelar",
                on_click=self._cancelar
            ),

            ft.ElevatedButton(
                "Eliminar Definitivamente",
                on_click=self._eliminar,
                bgcolor="#ef4444",
                color="white"
            )
        ]

        self.actions_alignment = ft.MainAxisAlignment.END

    def abrir(self, nombre_prod):

        self.producto_a_eliminar = nombre_prod

        self.txt_mensaje.value = (
            f"Estas a punto de eliminar '{nombre_prod}' "
            f"permanentemente.\nEstas seguro?"
        )

        self.open = True

        if self not in self.main_page.overlay:
            self.main_page.overlay.append(self)

        self.main_page.update()

    def _cancelar(self, e):
        self.open = False
        self.main_page.update()

    def _eliminar(self, e):

        if self.producto_a_eliminar:

            self.dm.eliminar_producto(
                self.producto_a_eliminar
            )

            self.open = False

            self.on_success(
                self.producto_a_eliminar
            )


class CartItemRow(ft.Row):

    def __init__(
        self,
        nombre_prod: str,
        precio: float,
        cantidad: int,
        on_change
    ):

        super().__init__(
            alignment="spaceBetween"
        )

        self.nombre_prod = nombre_prod
        self.precio = precio
        self.cantidad = cantidad
        self.on_change = on_change

        self.info_text = ft.Text(
            f"{self.nombre_prod} (${self.precio:.2f})",
            expand=True
        )

        self.btn_minus = ft.IconButton(
            icon=Icons.REMOVE,
            icon_color="#f87171",
            on_click=self._decrementar
        )

        self.txt_cantidad = ft.Text(
            str(self.cantidad),
            weight="bold",
            size=16,
            width=25,
            text_align="center"
        )

        self.btn_plus = ft.IconButton(
            icon=Icons.ADD,
            icon_color="#a3e635",
            on_click=self._incrementar
        )

        self.btn_delete = ft.IconButton(
            icon=Icons.DELETE,
            icon_color="#ef4444",
            on_click=self._eliminar
        )

        self.subtotal_text = ft.Text(
            f"${self.cantidad * self.precio:.2f}",
            weight="bold",
            width=60,
            text_align="right"
        )

        self.controls = [

            self.info_text,

            ft.Row([
                self.btn_minus,
                self.txt_cantidad,
                self.btn_plus
            ],
                tight=True,
                spacing=0
            ),

            self.subtotal_text,

            self.btn_delete
        ]

    def _decrementar(self, e):

        if self.cantidad > 1:

            self.cantidad -= 1

            self._actualizar_ui()

            self.on_change(
                self.nombre_prod,
                self.cantidad
            )

        else:
            self._eliminar(e)

    def _incrementar(self, e):

        self.cantidad += 1

        self._actualizar_ui()

        self.on_change(
            self.nombre_prod,
            self.cantidad
        )

    def _eliminar(self, e):

        self.cantidad = 0

        self.on_change(
            self.nombre_prod,
            self.cantidad
        )

    def _actualizar_ui(self):

        self.txt_cantidad.value = str(self.cantidad)

        self.subtotal_text.value = (
            f"${self.cantidad * self.precio:.2f}"
        )

        self.update()


class POSView(ft.Container):

    def __init__(self, page, data_manager):

        super().__init__(expand=True)

        self.main_page = page
        self.dm = data_manager

        # =========================
        # DATOS
        # =========================
        self.carrito = {}

        self.descuentos = []

        self.inventario = self.dm.get_inventario()

        # =========================
        # UI
        # =========================
        self.lista_ticket = ft.ListView(
            expand=True,
            spacing=10
        )

        self.txt_total = ft.Text(
            "$0.00",
            size=32,
            weight="bold",
            color="#38bdf8"
        )

        self.productos_grid = self._create_empty_grid()

        self.add_product_dialog = AddProductDialog(
            self.main_page,
            self.dm,
            self._on_product_added
        )

        self.add_discount_dialog = AddDiscountDialog(
            self.main_page,
            self.agregar_descuento
        )

        self.delete_product_dialog = DeleteProductDialog(
            self.main_page,
            self.dm,
            self._on_product_deleted
        )

        self.content = self._build_layout()

        self._renderizar_catalogo()

    def _create_empty_grid(self):

        return ft.GridView(
            expand=True,
            max_extent=250,
            child_aspect_ratio=1.2,
            spacing=15,
            run_spacing=15
        )

    def agregar_descuento(self, nombre, monto):

        if monto <= 0:
            return

        self.descuentos.append({
            "nombre": nombre,
            "monto": monto
        })

        self._update_ticket()

    def _renderizar_catalogo(self):

        self.productos_grid.controls.clear()

        # =========================
        # BOTON AGREGAR PLATILLO
        # =========================
        self.productos_grid.controls.append(

            ft.Card(
                content=ft.Container(

                    content=ft.Column([

                        ft.Text(
                            "Agregar Platillo",
                            weight="bold",
                            size=16
                        ),

                        ft.Text(
                            "+",
                            size=24,
                            weight="bold",
                            color="#a3e635"
                        )

                    ],
                        alignment="center",
                        horizontal_alignment="center"
                    ),

                    padding=10,
                    ink=True,
                    on_click=self._abrir_dialogo_producto,
                    bgcolor="#1e293b",
                    border_radius=10
                )
            )
        )

        # =========================
        # PRODUCTOS
        # =========================
        for prod, data in self.inventario.items():

            self.productos_grid.controls.append(

                ft.Card(
                    content=ft.Container(

                        content=ft.Column([

                            ft.Text(
                                prod,
                                weight="bold",
                                size=16,
                                text_align="center"
                            ),

                            ft.Row([

                                ft.Text(
                                    f"${data['precio']}",
                                    color="#38bdf8",
                                    size=18
                                ),

                                ft.IconButton(
                                    icon=Icons.DELETE,
                                    icon_color="#ef4444",
                                    icon_size=18,
                                    on_click=lambda e, p=prod:
                                    self.delete_product_dialog.abrir(p)
                                )

                            ],
                                alignment="center",
                                tight=True
                            )

                        ],
                            alignment="center",
                            horizontal_alignment="center"
                        ),

                        padding=10,
                        ink=True,
                        bgcolor="#1e293b",
                        border_radius=10,

                        on_click=lambda e, p=prod:
                        self._add_to_cart(p, e)
                    )
                )
            )

        try:
            self.update()

        except RuntimeError:
            pass

    def _abrir_dialogo_producto(self, e):

        if self.add_product_dialog not in self.main_page.overlay:
            self.main_page.overlay.append(
                self.add_product_dialog
            )

        self.add_product_dialog.open = True

        self.main_page.update()

    def _abrir_dialogo_descuento(self, e):

        if self.add_discount_dialog not in self.main_page.overlay:
            self.main_page.overlay.append(
                self.add_discount_dialog
            )

        self.add_discount_dialog.open = True

        self.main_page.update()

    def _on_product_added(self):

        self.inventario = self.dm.get_inventario()

        self._renderizar_catalogo()

    def _on_product_deleted(self, nombre_eliminado):

        self.inventario = self.dm.get_inventario()

        if nombre_eliminado in self.carrito:
            del self.carrito[nombre_eliminado]

            self._update_ticket()

        self._renderizar_catalogo()

    def _add_to_cart(self, prod, e):

        self.carrito[prod] = (
            self.carrito.get(prod, 0) + 1
        )

        self._update_ticket()

    def _on_cart_item_change(self, prod, nueva_cantidad):

        if nueva_cantidad <= 0:

            if prod in self.carrito:
                del self.carrito[prod]

        else:
            self.carrito[prod] = nueva_cantidad

        self._update_ticket()

    def _update_ticket(self):

        self.lista_ticket.controls.clear()

        subtotal = 0

        # =========================
        # PRODUCTOS
        # =========================
        for prod, cant in list(self.carrito.items()):

            if cant > 0:

                precio = self.inventario[prod]["precio"]

                sub = cant * precio

                subtotal += sub

                item_row = CartItemRow(
                    nombre_prod=prod,
                    precio=precio,
                    cantidad=cant,
                    on_change=self._on_cart_item_change
                )

                self.lista_ticket.controls.append(
                    item_row
                )

        # =========================
        # DESCUENTOS
        # =========================
        total_descuentos = 0

        if self.descuentos:

            self.lista_ticket.controls.append(
                ft.Divider()
            )

        for desc in self.descuentos:

            total_descuentos += desc["monto"]

            self.lista_ticket.controls.append(

                ft.Row(
                    alignment="spaceBetween",

                    controls=[

                        ft.Text(
                            f"DESCUENTO: {desc['nombre']}",
                            color="#f87171",
                            weight="bold"
                        ),

                        ft.Text(
                            f"-${desc['monto']:.2f}",
                            color="#f87171",
                            weight="bold"
                        )
                    ]
                )
            )

        # =========================
        # TOTAL
        # =========================
        total = subtotal - total_descuentos

        if total < 0:
            total = 0

        self.txt_total.value = f"${total:.2f}"

        self.update()

    def _cobrar(self, e):

        total = (
            sum(
                self.carrito[p] *
                self.inventario[p]["precio"]
                for p in self.carrito
            )
            -
            sum(
                d["monto"]
                for d in self.descuentos
            )
        )

        if total < 0:
            total = 0

        if total > 0:

            self.dm.registrar_venta(

                {
                    k: v
                    for k, v in self.carrito.items()
                    if v > 0
                },

                total
            )

            self.carrito.clear()

            self.descuentos.clear()

            self.inventario = self.dm.get_inventario()

            self._update_ticket()

            snack = ft.SnackBar(
                ft.Text("✅ Cobro exitoso"),
                bgcolor="#166534"
            )

            self.main_page.overlay.append(snack)

            snack.open = True

            self.main_page.update()

    def _deshacer(self, e):

        resultado = self.dm.deshacer_ultima_venta()

        if resultado:

            self.inventario = self.dm.get_inventario()

            snack = ft.SnackBar(
                ft.Text(
                    f"↩ Ultima venta "
                    f"(${resultado['total']:.2f}) "
                    f"deshecha"
                ),
                bgcolor="#92400e"
            )

        else:

            snack = ft.SnackBar(
                ft.Text(
                    "⚠ No hay ventas para deshacer"
                ),
                bgcolor="#475569"
            )

        self.main_page.overlay.append(snack)

        snack.open = True

        self.main_page.update()

        self.update()

    def _build_layout(self):

        panel_cobro = ft.Container(

            width=430,

            padding=20,

            bgcolor="#1e293b",

            border_radius=10,

            content=ft.Column([

                ft.Text(
                    "ORDEN ACTUAL",
                    size=20,
                    weight="bold"
                ),

                ft.Divider(),

                self.lista_ticket,

                ft.Divider(),

                ft.Row([

                    ft.Text(
                        "TOTAL",
                        size=20
                    ),

                    self.txt_total

                ],
                    alignment="spaceBetween"
                ),

                ft.Container(height=10),

                # =========================
                # BOTON DESCUENTO
                # =========================
                ft.ElevatedButton(
                    "AGREGAR DESCUENTO",
                    on_click=self._abrir_dialogo_descuento,
                    bgcolor="#f87171",
                    color="white",
                    height=50,
                    width=float('inf')
                ),

                ft.Container(height=8),

                # =========================
                # BOTON COBRAR
                # =========================
                ft.ElevatedButton(
                    "COBRAR",
                    on_click=self._cobrar,
                    bgcolor="#38bdf8",
                    color="#0f172a",
                    height=60,
                    width=float('inf')
                ),

                ft.Container(height=6),

                ft.OutlinedButton(
                    "↩ Deshacer ultima venta",
                    on_click=self._deshacer,
                    width=float('inf'),
                    height=44
                ),

            ],
                expand=True
            )
        )

        return ft.Row([

            ft.Container(
                content=self.productos_grid,
                expand=True,
                padding=20
            ),

            panel_cobro

        ],
            expand=True
        )