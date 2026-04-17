"""
migrate_json_to_sqlite.py
Script de migracion ONE-TIME: lee los archivos JSON existentes
y los inserta en la base de datos SQLite (pos.db).

Uso desde la raiz del proyecto:
    py -m core.migrate_json_to_sqlite

Los archivos JSON originales NO se eliminan (quedan como respaldo).
Si la BD ya tiene datos, el script muestra advertencia pero no falla.
"""

import json
import os
import sqlite3
from datetime import datetime

# -- Rutas --------------------------------------------------------------------
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, "..", "data")
DB_PATH    = os.path.join(DATA_DIR, "pos.db")

F_INVENTARIO = os.path.join(DATA_DIR, "inventario.json")
F_VENTAS     = os.path.join(DATA_DIR, "ventas.json")
F_GASTOS     = os.path.join(DATA_DIR, "gastos.json")
DIR_CIERRES  = os.path.join(DATA_DIR, "cierres")


# -- Helpers ------------------------------------------------------------------
def cargar_json(ruta, default):
    if not os.path.exists(ruta):
        print(f"  [!] No encontrado: {ruta}  (se omite)")
        return default
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# -- Migracion ----------------------------------------------------------------
def migrar_inventario(conn: sqlite3.Connection):
    print("\nMigrando inventario...")
    inventario = cargar_json(F_INVENTARIO, {})
    insertados = 0
    omitidos   = 0
    for nombre, data in inventario.items():
        try:
            conn.execute(
                "INSERT INTO productos (nombre, precio, stock) VALUES (?, ?, ?)",
                (nombre, data.get("precio", 0), data.get("stock", 100))
            )
            insertados += 1
        except sqlite3.IntegrityError:
            # El producto ya existe (p.ej. si se ejecuta el script dos veces)
            omitidos += 1
    print(f"  [OK] Insertados: {insertados}  |  Omitidos (ya existian): {omitidos}")


def migrar_ventas(conn: sqlite3.Connection):
    print("\nMigrando ventas...")
    ventas = cargar_json(F_VENTAS, [])
    insertadas = 0
    for v in ventas:
        fecha = v.get("fecha", datetime.now().strftime("%Y-%m-%d"))
        hora  = v.get("hora",  "00:00")
        total = v.get("total", 0)

        cursor = conn.execute(
            "INSERT INTO ventas (fecha, hora, total) VALUES (?, ?, ?)",
            (fecha, hora, total)
        )
        venta_id = cursor.lastrowid

        for prod, cant in v.get("productos", {}).items():
            conn.execute(
                "INSERT INTO venta_detalle (venta_id, producto, cantidad) VALUES (?, ?, ?)",
                (venta_id, prod, cant)
            )
        insertadas += 1
    print(f"  [OK] Ventas insertadas: {insertadas}")


def migrar_gastos(conn: sqlite3.Connection):
    print("\nMigrando gastos...")
    gastos = cargar_json(F_GASTOS, [])
    insertados = 0
    for g in gastos:
        conn.execute(
            "INSERT INTO gastos (fecha, concepto, monto) VALUES (?, ?, ?)",
            (g.get("fecha", ""), g.get("concepto", ""), g.get("monto", 0))
        )
        insertados += 1
    print(f"  [OK] Gastos insertados: {insertados}")


def migrar_cierres(conn: sqlite3.Connection):
    print("\nMigrando cierres de dia...")
    if not os.path.exists(DIR_CIERRES):
        print("  [!] Carpeta cierres/ no encontrada (se omite)")
        return
    insertados = 0
    omitidos   = 0
    for archivo in os.listdir(DIR_CIERRES):
        if not archivo.endswith(".json"):
            continue
        ruta = os.path.join(DIR_CIERRES, archivo)
        cierre = cargar_json(ruta, {})
        try:
            conn.execute(
                """INSERT INTO cierres (fecha, ventas, gastos, ganancia)
                   VALUES (?, ?, ?, ?)""",
                (
                    cierre.get("fecha", archivo.replace(".json", "")),
                    cierre.get("ventas",   0),
                    cierre.get("gastos",   0),
                    cierre.get("ganancia", 0),
                )
            )
            insertados += 1
        except sqlite3.IntegrityError:
            omitidos += 1
    print(f"  [OK] Cierres insertados: {insertados}  |  Omitidos: {omitidos}")


def verificar_resultado(conn: sqlite3.Connection):
    print("\nResumen final en SQLite:")
    tablas = ["productos", "ventas", "venta_detalle", "gastos", "cierres"]
    for t in tablas:
        n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t:<20} -> {n} registros")


def seed_data_si_esta_vacio(conn: sqlite3.Connection):
    count = conn.execute("SELECT COUNT(*) FROM productos").fetchone()[0]
    if count == 0:
        print("\n  [!] El inventario esta vacio despues de la migracion.")
        print("  Insertando datos genericos de prueba...")
        productos_base = [
            ("Producto de Ejemplo A", 15.50, 100),
            ("Producto de Ejemplo B", 25.00, 100),
            ("Producto de Ejemplo C", 50.00, 100),
        ]
        conn.executemany(
            "INSERT OR IGNORE INTO productos (nombre, precio, stock) VALUES (?, ?, ?)",
            productos_base
        )
        print("  [OK] Datos de prueba insertados.")


def main():
    print("=" * 55)
    print("  MIGRACION JSON -> SQLite  -  Sistema POS")
    print("=" * 55)
    print(f"\n  Base de datos: {DB_PATH}")

    # Verificar si la BD ya tiene datos para advertir al usuario
    with get_conn() as conn:
        try:
            total_existente = conn.execute("SELECT COUNT(*) FROM ventas").fetchone()[0]
            if total_existente > 0:
                print(f"\n  ADVERTENCIA: La tabla 'ventas' ya tiene {total_existente} registros.")
                print("  Si continuas, podrias duplicar los datos.")
                resp = input("  Continuar de todas formas? (s/N): ").strip().lower()
                if resp != "s":
                    print("\n  Migracion cancelada por el usuario.")
                    return
        except sqlite3.OperationalError:
            pass  # Las tablas aun no existen; se crearan al instanciar DataManager

    # Importar DataManager para que cree las tablas si no existen
    from core.data_manager import DataManager
    DataManager()  # Solo para _inicializar_bd()

    with get_conn() as conn:
        migrar_inventario(conn)
        migrar_ventas(conn)
        migrar_gastos(conn)
        migrar_cierres(conn)
        seed_data_si_esta_vacio(conn)
        verificar_resultado(conn)

    print("\n[OK] Migracion completada exitosamente!")
    print("   Los archivos JSON originales se conservan como respaldo.")
    print("=" * 55)


if __name__ == "__main__":
    main()
