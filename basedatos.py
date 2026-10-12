from turso_http import ejecutar


def crear_tablas():
    ejecutar("""
        CREATE TABLE IF NOT EXISTS cuentas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            banco TEXT,
            tipo TEXT NOT NULL,
            saldo_inicial REAL NOT NULL,
            saldo_actual REAL NOT NULL
        )
    """)

    ejecutar("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo TEXT NOT NULL
        )
    """)

    ejecutar("""
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            cuenta TEXT NOT NULL,
            categoria TEXT,
            tipo TEXT NOT NULL,
            importe REAL NOT NULL,
            cuenta_destino TEXT,
            nota TEXT
        )
    """)

    ejecutar("""
        CREATE TABLE IF NOT EXISTS presupuesto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT NOT NULL,
            mes TEXT NOT NULL,
            presupuesto REAL NOT NULL
        )
    """)

    ejecutar("""
        CREATE TABLE IF NOT EXISTS recurrentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT NOT NULL,
            cuenta TEXT NOT NULL,
            categoria TEXT,
            tipo TEXT NOT NULL,
            importe REAL NOT NULL,
            cuenta_destino TEXT,
            dia_del_mes INTEGER NOT NULL,
            mes_inicio TEXT NOT NULL,
            cuotas_totales INTEGER NOT NULL
        )
    """)


# ---------- CUENTAS ----------

def insertar_cuenta(nombre, banco, tipo, saldo_inicial):
    ejecutar(
        "INSERT INTO cuentas (nombre, banco, tipo, saldo_inicial, saldo_actual) VALUES (?, ?, ?, ?, ?)",
        (nombre.strip(), banco, tipo, saldo_inicial, saldo_inicial)
    )


def obtener_cuentas():
    filas, _ = ejecutar("SELECT id, nombre, banco, tipo, saldo_inicial, saldo_actual FROM cuentas ORDER BY nombre ASC")
    return filas


def actualizar_cuenta(id_cuenta, nombre, banco, tipo, saldo_inicial):
    nombre = nombre.strip()
    filas, _ = ejecutar("SELECT nombre FROM cuentas WHERE id = ?", (id_cuenta,))
    nombre_viejo = filas[0]["nombre"] if filas else None

    ejecutar(
        "UPDATE cuentas SET nombre = ?, banco = ?, tipo = ?, saldo_inicial = ? WHERE id = ?",
        (nombre, banco, tipo, saldo_inicial, id_cuenta)
    )

    if nombre_viejo and nombre_viejo != nombre:
        for tabla in ["movimientos", "recurrentes", "movimientos_archivo"]:
            ejecutar(f"UPDATE {tabla} SET cuenta = ? WHERE cuenta = ?", (nombre, nombre_viejo))
            ejecutar(f"UPDATE {tabla} SET cuenta_destino = ? WHERE cuenta_destino = ?", (nombre, nombre_viejo))


def eliminar_cuenta(id_cuenta):
    ejecutar("DELETE FROM cuentas WHERE id = ?", (id_cuenta,))


# ---------- CATEGORIAS ----------

def insertar_categoria(nombre, tipo):
    ejecutar(
        "INSERT INTO categorias (nombre, tipo) VALUES (?, ?)",
        (nombre, tipo)
    )


def obtener_categorias():
    filas, _ = ejecutar("SELECT id, nombre, tipo FROM categorias")
    return filas


def actualizar_categoria(id_categoria, nombre, tipo):
    ejecutar(
        "UPDATE categorias SET nombre = ?, tipo = ? WHERE id = ?",
        (nombre, tipo, id_categoria)
    )


def eliminar_categoria(id_categoria):
    ejecutar("DELETE FROM categorias WHERE id = ?", (id_categoria,))


# ---------- MOVIMIENTOS ----------

def insertar_movimiento(fecha, cuenta, categoria, tipo, importe, cuenta_destino, nota):
    ejecutar(
        "INSERT INTO movimientos (fecha, cuenta, categoria, tipo, importe, cuenta_destino, nota) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (fecha, cuenta, categoria, tipo, abs(float(importe)), cuenta_destino, nota)

    )


def obtener_movimientos():
    filas, _ = ejecutar("SELECT id, fecha, cuenta, categoria, tipo, importe, cuenta_destino, nota FROM movimientos")
    return filas


def actualizar_movimiento(id_movimiento, fecha, cuenta, categoria, tipo, importe, cuenta_destino, nota):
    ejecutar(
        "UPDATE movimientos SET fecha = ?, cuenta = ?, categoria = ?, tipo = ?, importe = ?, cuenta_destino = ?, nota = ? WHERE id = ?",
        (fecha, cuenta, categoria, tipo, abs(float(importe)), cuenta_destino, nota, id_movimiento)
    )


def eliminar_movimiento(id_movimiento):
    ejecutar("DELETE FROM movimientos WHERE id = ?", (id_movimiento,))


# ---------- PRESUPUESTO ----------

def insertar_presupuesto(categoria, mes, presupuesto):
    ejecutar(
        "INSERT INTO presupuesto (categoria, mes, presupuesto) VALUES (?, ?, ?)",
        (categoria, mes, presupuesto)
    )


def obtener_presupuesto():
    filas, _ = ejecutar("SELECT id, categoria, mes, presupuesto FROM presupuesto")
    return filas


def actualizar_presupuesto(id_presupuesto, categoria, mes, presupuesto):
    ejecutar(
        "UPDATE presupuesto SET categoria = ?, mes = ?, presupuesto = ? WHERE id = ?",
        (categoria, mes, presupuesto, id_presupuesto)
    )


def eliminar_presupuesto(id_presupuesto):
    ejecutar("DELETE FROM presupuesto WHERE id = ?", (id_presupuesto,))


# ---------- RECURRENTES ----------

def insertar_recurrente(descripcion, cuenta, categoria, tipo, importe, cuenta_destino, dia_del_mes, mes_inicio, cuotas_totales):
    ejecutar(
        "INSERT INTO recurrentes (descripcion, cuenta, categoria, tipo, importe, cuenta_destino, dia_del_mes, mes_inicio, cuotas_totales) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (descripcion, cuenta, categoria, tipo, abs(float(importe)), cuenta_destino, dia_del_mes, mes_inicio, cuotas_totales)
    
    )


def obtener_recurrentes():
    filas, _ = ejecutar("SELECT id, descripcion, cuenta, categoria, tipo, importe, cuenta_destino, dia_del_mes, mes_inicio, cuotas_totales, cuotas_previas FROM recurrentes")
    return filas


def actualizar_recurrente(id_recurrente, descripcion, cuenta, categoria, tipo, importe, cuenta_destino, dia_del_mes, mes_inicio, cuotas_totales):
    ejecutar(
        "UPDATE recurrentes SET descripcion = ?, cuenta = ?, categoria = ?, tipo = ?, importe = ?, cuenta_destino = ?, dia_del_mes = ?, mes_inicio = ?, cuotas_totales = ? WHERE id = ?",
        (descripcion, cuenta, categoria, tipo, abs(float(importe)), cuenta_destino, dia_del_mes, mes_inicio, cuotas_totales, id_recurrente)
    )

def actualizar_cuotas_previas(id_recurrente, cuotas_previas):
    ejecutar("UPDATE recurrentes SET cuotas_previas = ? WHERE id = ?", (int(cuotas_previas), id_recurrente))


def eliminar_recurrente(id_recurrente):
    ejecutar("DELETE FROM recurrentes WHERE id = ?", (id_recurrente,))


def crear_tabla_archivo():
    ejecutar("""
        CREATE TABLE IF NOT EXISTS movimientos_archivo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            anio TEXT NOT NULL,
            fecha TEXT NOT NULL,
            cuenta TEXT NOT NULL,
            categoria TEXT,
            tipo TEXT NOT NULL,
            importe REAL NOT NULL,
            cuenta_destino TEXT,
            nota TEXT
        )
    """)


if __name__ == "__main__":
    crear_tablas()
    crear_tabla_archivo()
    print("Tablas creadas correctamente en Turso.")


def insertar_movimiento_archivo(anio, fecha, cuenta, categoria, tipo, importe, cuenta_destino, nota):
    ejecutar(
        "INSERT INTO movimientos_archivo (anio, fecha, cuenta, categoria, tipo, importe, cuenta_destino, nota) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (anio, fecha, cuenta, categoria, tipo, importe, cuenta_destino, nota)
    )


def obtener_movimientos_archivo(anio=None):
    if anio:
        filas, _ = ejecutar("SELECT * FROM movimientos_archivo WHERE anio = ?", (anio,))
    else:
        filas, _ = ejecutar("SELECT * FROM movimientos_archivo")
    return filas

# ---------- PLANIFICACION ----------

def crear_tabla_planificacion():
    ejecutar("""
        CREATE TABLE IF NOT EXISTS plan_mes (
            mes TEXT PRIMARY KEY,
            saldo_partida REAL,
            fecha_saldo TEXT,
            otros_ingresos REAL NOT NULL DEFAULT 0
        )
    """)


def obtener_plan_mes(mes):
    filas, _ = ejecutar("SELECT mes, saldo_partida, fecha_saldo, otros_ingresos FROM plan_mes WHERE mes = ?", (mes,))
    return filas[0] if filas else None


def guardar_plan_mes(mes, saldo_partida, fecha_saldo, otros_ingresos):
    ejecutar(
        "INSERT INTO plan_mes (mes, saldo_partida, fecha_saldo, otros_ingresos) VALUES (?, ?, ?, ?) "
        "ON CONFLICT(mes) DO UPDATE SET saldo_partida = excluded.saldo_partida, "
        "fecha_saldo = excluded.fecha_saldo, otros_ingresos = excluded.otros_ingresos",
        (mes, saldo_partida, fecha_saldo, otros_ingresos)
    )

def crear_tabla_plan_items():
    ejecutar("""
        CREATE TABLE IF NOT EXISTS plan_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mes TEXT NOT NULL,
            grupo TEXT NOT NULL,
            descripcion TEXT,
            fecha TEXT,
            cuenta TEXT,
            cuenta_destino TEXT,
            categoria TEXT,
            importe REAL NOT NULL DEFAULT 0,
            movimiento_id INTEGER
        )
    """)


def obtener_plan_items(mes, grupo):
    filas, _ = ejecutar("SELECT * FROM plan_items WHERE mes = ? AND grupo = ? ORDER BY fecha, id", (mes, grupo))
    return filas


def insertar_plan_item(mes, grupo, descripcion, fecha, cuenta, cuenta_destino, categoria, importe):
    ejecutar(
        "INSERT INTO plan_items (mes, grupo, descripcion, fecha, cuenta, cuenta_destino, categoria, importe) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (mes, grupo, descripcion, fecha, cuenta, cuenta_destino, categoria, abs(float(importe or 0)))
    )


def actualizar_plan_item(id_item, descripcion, fecha, cuenta, cuenta_destino, categoria, importe):
    ejecutar(
        "UPDATE plan_items SET descripcion = ?, fecha = ?, cuenta = ?, cuenta_destino = ?, categoria = ?, importe = ? WHERE id = ?",
        (descripcion, fecha, cuenta, cuenta_destino, categoria, abs(float(importe or 0)), id_item)
    )


def vincular_plan_item(id_item, movimiento_id):
    ejecutar("UPDATE plan_items SET movimiento_id = ? WHERE id = ?", (movimiento_id, id_item))


def eliminar_plan_item(id_item):
    ejecutar("DELETE FROM plan_items WHERE id = ?", (id_item,))


def obtener_ultimo_movimiento_id(nota, fecha):
    filas, _ = ejecutar("SELECT id FROM movimientos WHERE nota = ? AND fecha = ? ORDER BY id DESC LIMIT 1", (nota, fecha))
    return int(filas[0]["id"]) if filas else None