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
        (nombre, banco, tipo, saldo_inicial, saldo_inicial)
    )


def obtener_cuentas():
    filas, _ = ejecutar("SELECT id, nombre, banco, tipo, saldo_inicial, saldo_actual FROM cuentas")
    return filas


def actualizar_cuenta(id_cuenta, nombre, banco, tipo, saldo_inicial):
    ejecutar(
        "UPDATE cuentas SET nombre = ?, banco = ?, tipo = ?, saldo_inicial = ? WHERE id = ?",
        (nombre, banco, tipo, saldo_inicial, id_cuenta)
    )


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
        (fecha, cuenta, categoria, tipo, importe, cuenta_destino, nota)
    )


def obtener_movimientos():
    filas, _ = ejecutar("SELECT id, fecha, cuenta, categoria, tipo, importe, cuenta_destino, nota FROM movimientos")
    return filas


def actualizar_movimiento(id_movimiento, fecha, cuenta, categoria, tipo, importe, cuenta_destino, nota):
    ejecutar(
        "UPDATE movimientos SET fecha = ?, cuenta = ?, categoria = ?, tipo = ?, importe = ?, cuenta_destino = ?, nota = ? WHERE id = ?",
        (fecha, cuenta, categoria, tipo, importe, cuenta_destino, nota, id_movimiento)
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
        (descripcion, cuenta, categoria, tipo, importe, cuenta_destino, dia_del_mes, mes_inicio, cuotas_totales)
    )


def obtener_recurrentes():
    filas, _ = ejecutar("SELECT id, descripcion, cuenta, categoria, tipo, importe, cuenta_destino, dia_del_mes, mes_inicio, cuotas_totales FROM recurrentes")
    return filas


def actualizar_recurrente(id_recurrente, descripcion, cuenta, categoria, tipo, importe, cuenta_destino, dia_del_mes, mes_inicio, cuotas_totales):
    ejecutar(
        "UPDATE recurrentes SET descripcion = ?, cuenta = ?, categoria = ?, tipo = ?, importe = ?, cuenta_destino = ?, dia_del_mes = ?, mes_inicio = ?, cuotas_totales = ? WHERE id = ?",
        (descripcion, cuenta, categoria, tipo, importe, cuenta_destino, dia_del_mes, mes_inicio, cuotas_totales, id_recurrente)
    )


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