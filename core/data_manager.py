import json
import os
from datetime import datetime

class DataManager:
    """
    Capa de Acceso a Datos (DAL) para el sistema de Punto de Venta.
    Controla la persistencia de ventas, inventario y cierres en archivos JSON locales.
    """
    def __init__(self):
        # En Android/iOS, Flet expone FLET_APP_STORAGE como carpeta de escritura segura.
        # En desktop, usamos la carpeta /data del proyecto.
        mobile_storage = os.environ.get("FLET_APP_STORAGE")
        if mobile_storage:
            self.dir_data = os.path.join(mobile_storage, "data")
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.dir_data = os.path.join(base_dir, "..", "data")
        os.makedirs(self.dir_data, exist_ok=True)
            
        self.f_ventas = f"{self.dir_data}/ventas.json"
        self.f_gastos = f"{self.dir_data}/gastos.json"
        self.f_inventario = f"{self.dir_data}/inventario.json"
        self.dir_cierres = os.path.join(self.dir_data, "cierres")
        os.makedirs(self.dir_cierres, exist_ok=True)
        self._inicializar_inventario()

    def _cargar(self, archivo):
        if not os.path.exists(archivo): return [] if "inventario" not in archivo else {}
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return [] if "inventario" not in archivo else {}

    def _guardar(self, archivo, data):
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _inicializar_inventario(self):
        inv = self._cargar(self.f_inventario)
        # Productos base con stock inicial de 100
        base = {
            "Molote Pollo": {"precio": 20, "stock": 100},
            "Molote Queso": {"precio": 20, "stock": 100},
            "Molote Hawaiano": {"precio": 20, "stock": 100},
            "Quesadilla Papa": {"precio": 10, "stock": 100},
            "Quesadilla Pollo": {"precio": 10, "stock": 100},
            "Tostada Sencilla": {"precio": 10, "stock": 100}
        }
        if not inv:
            self._guardar(self.f_inventario, base)

    def get_inventario(self) -> dict:
        """Retorna el diccionario con todo el inventario de productos."""
        return self._cargar(self.f_inventario)

    def agregar_producto(self, nombre: str, precio: float, stock: int = 100) -> bool:
        """
        Agrega un nuevo producto al inventario.
        Retorna True si la operación fue exitosa, o False si el producto ya existía.
        """
        inv = self.get_inventario()
        # Verificamos si ya existe para no sobreescribirlo accidentalmente
        if nombre in inv:
            return False
        
        inv[nombre] = {"precio": precio, "stock": stock}
        self._guardar(self.f_inventario, inv)
        return True

    def eliminar_producto(self, nombre: str) -> bool:
        """
        Elimina un producto del inventario de forma permanente.
        """
        inv = self.get_inventario()
        if nombre in inv:
            del inv[nombre]
            self._guardar(self.f_inventario, inv)
            return True
        return False

    def registrar_venta(self, carrito: dict, total: float):
        """Registra una venta con su estampa de tiempo y la resta del inventario."""
        # Guardar venta
        ahora = datetime.now()
        venta = {
            "fecha": ahora.strftime("%Y-%m-%d"),
            "hora": ahora.strftime("%H:%M"),
            "productos": carrito,
            "total": total
        }
        ventas = self._cargar(self.f_ventas)
        ventas.append(venta)
        self._guardar(self.f_ventas, ventas)

        # Descontar inventario
        inv = self.get_inventario()
        for prod, cant in carrito.items():
            if prod in inv:
                inv[prod]["stock"] -= cant
        self._guardar(self.f_inventario, inv)

    def deshacer_ultima_venta(self):
        """Elimina la última venta y restaura el stock correspondiente."""
        ventas = self._cargar(self.f_ventas)
        if not ventas:
            return False
        ultima = ventas.pop()
        self._guardar(self.f_ventas, ventas)

        # Restaurar inventario
        inv = self.get_inventario()
        for prod, cant in ultima.get("productos", {}).items():
            if prod in inv:
                inv[prod]["stock"] += cant
        self._guardar(self.f_inventario, inv)
        return ultima

    def get_historial_hoy(self):
        """Retorna lista de ventas del día actual con hora y total."""
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        ventas = self._cargar(self.f_ventas)
        return [v for v in ventas if v.get("fecha") == fecha_hoy]

    def cerrar_dia(self):
        """Calcula el resumen del día y lo guarda en data/cierres/YYYY-MM-DD.json."""
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        ventas = self._cargar(self.f_ventas)
        gastos = self._cargar(self.f_gastos)

        total_ventas = sum(v["total"] for v in ventas if v.get("fecha") == fecha_hoy)
        total_gastos = sum(g["monto"] for g in gastos if g.get("fecha") == fecha_hoy)
        ganancia = total_ventas - total_gastos

        resumen = {
            "fecha": fecha_hoy,
            "ventas": round(total_ventas, 2),
            "gastos": round(total_gastos, 2),
            "ganancia": round(ganancia, 2)
        }
        ruta = os.path.join(self.dir_cierres, f"{fecha_hoy}.json")
        self._guardar(ruta, resumen)
        return resumen, ruta

    def registrar_gasto(self, concepto, monto):
        gasto = {
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "concepto": concepto,
            "monto": monto
        }
        gastos = self._cargar(self.f_gastos)
        gastos.append(gasto)
        self._guardar(self.f_gastos, gastos)

    def get_historico_7_dias(self):
        from datetime import timedelta
        ventas = self._cargar(self.f_ventas)
        resultado = []
        hoy = datetime.now().date()
        for i in range(6, -1, -1):
            dia = hoy - timedelta(days=i)
            fecha_str = dia.strftime("%Y-%m-%d")
            total_dia = sum(v["total"] for v in ventas if v.get("fecha") == fecha_str)
            resultado.append({"fecha": dia.strftime("%d/%m"), "total": total_dia})
        return resultado

    def get_kpis_y_graficos(self):
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        ventas = self._cargar(self.f_ventas)
        gastos = self._cargar(self.f_gastos)
        
        ventas_hoy = [v for v in ventas if v.get("fecha") == fecha_hoy]
        total_v = sum(v["total"] for v in ventas_hoy)
        total_g = sum(g["monto"] for g in gastos if g.get("fecha") == fecha_hoy)
        
        # Productos más vendidos hoy
        conteo = {}
        for v in ventas_hoy:
            for p, c in v["productos"].items():
                conteo[p] = conteo.get(p, 0) + c
        
        return {
            "ventas_hoy": total_v,
            "gastos_hoy": total_g,
            "ganancia": total_v - total_g,
            "top_productos": conteo
        }