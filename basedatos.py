import sqlite3

def conectar():
    conexion = sqlite3.connect("haushalt.db")
    return conexion

def crear_tablas():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cuentas (

            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            banco TEXT,
            tipo TEXT NOT NULL,
            saldo_inicial REAL NOT NULL,
            saldo_actual REAL NOT NULL
        )
    """)

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo TEXT NOT NULL
            )
    """)

    cursor.execute("""
                   
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

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS presupuesto (

            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT NOT NULL,
            mes TEXT NOT NULL,
            presupuesto REAL NOT NULL
    )
""")

    cursor.execute("""

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
    

    conexion.commit()
    conexion.close()

def insertar_categoria(nombre, tipo):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO categorias (nombre, tipo) VALUES (?, ?)",
        (nombre, tipo)
    )
    conexion.commit()
    conexion.close()


def obtener_categorias():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, tipo FROM categorias")
    filas = cursor.fetchall()
    conexion.close()

    categorias = []
    for fila in filas:
        categorias.append({"id": fila[0], "nombre": fila[1], "tipo": fila[2]})
    return categorias

def insertar_movimiento(fecha, cuenta, categoria, tipo, importe, cuenta_destino, nota):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO movimientos (fecha, cuenta, categoria, tipo, importe, cuenta_destino, nota) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (fecha, cuenta, categoria, tipo, importe, cuenta_destino, nota)
    )
    conexion.commit()
    conexion.close()


def obtener_movimientos():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, fecha, cuenta, categoria, tipo, importe, cuenta_destino, nota FROM movimientos")
    filas = cursor.fetchall()
    conexion.close()

    movimientos = []
    for fila in filas:
        movimientos.append({
            "id": fila[0], "fecha": fila[1], "cuenta": fila[2], "categoria": fila[3],
            "tipo": fila[4], "importe": fila[5], "cuenta_destino": fila[6], "nota": fila[7]
        })
    return movimientos


def insertar_presupuesto(categoria, mes, presupuesto):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO presupuesto (categoria, mes, presupuesto) VALUES (?, ?, ?)",
        (categoria, mes, presupuesto)
    )
    conexion.commit()
    conexion.close()


def obtener_presupuesto():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, categoria, mes, presupuesto FROM presupuesto")
    filas = cursor.fetchall()
    conexion.close()

    presupuesto = []
    for fila in filas:
        presupuesto.append({"id": fila[0], "categoria": fila[1], "mes": fila[2], "presupuesto": fila[3]})
    return presupuesto


def insertar_recurrente(descripcion, cuenta, categoria, tipo, importe, cuenta_destino, dia_del_mes, mes_inicio, cuotas_totales):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO recurrentes (descripcion, cuenta, categoria, tipo, importe, cuenta_destino, dia_del_mes, mes_inicio, cuotas_totales) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (descripcion, cuenta, categoria, tipo, importe, cuenta_destino, dia_del_mes, mes_inicio, cuotas_totales)
    )
    conexion.commit()
    conexion.close()


def obtener_recurrentes():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, descripcion, cuenta, categoria, tipo, importe, cuenta_destino, dia_del_mes, mes_inicio, cuotas_totales FROM recurrentes")
    filas = cursor.fetchall()
    conexion.close()

    recurrentes = []
    for fila in filas:
        recurrentes.append({
            "id": fila[0], "descripcion": fila[1], "cuenta": fila[2], "categoria": fila[3],
            "tipo": fila[4], "importe": fila[5], "cuenta_destino": fila[6],
            "dia_del_mes": fila[7], "mes_inicio": fila[8], "cuotas_totales": fila[9]
        })
    return recurrentes

def insertar_cuenta(nombre, banco, tipo, saldo_inicial):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO cuentas (nombre, banco, tipo, saldo_inicial, saldo_actual) VALUES (?, ?, ?, ?, ?)",
        (nombre, banco, tipo, saldo_inicial, saldo_inicial)
    )
    conexion.commit()
    conexion.close()


def obtener_cuentas():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, banco, tipo, saldo_inicial, saldo_actual FROM cuentas")
    filas = cursor.fetchall()
    conexion.close()

    cuentas = []
    for fila in filas:
        cuentas.append({
            "id": fila[0],
            "nombre": fila[1],
            "banco": fila[2],
            "tipo": fila[3],
            "saldo_inicial": fila[4],
            "saldo_actual": fila[5]
        })
    return cuentas

if __name__ == "__main__":
    crear_tablas()

def actualizar_movimiento(id_movimiento, fecha, cuenta, categoria, tipo, importe, cuenta_destino, nota):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE movimientos SET fecha = ?, cuenta = ?, categoria = ?, tipo = ?, importe = ?, cuenta_destino = ?, nota = ? WHERE id = ?",
        (fecha, cuenta, categoria, tipo, importe, cuenta_destino, nota, id_movimiento)
    )
    conexion.commit()
    conexion.close()


def eliminar_movimiento(id_movimiento):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM movimientos WHERE id = ?", (id_movimiento,))
    conexion.commit()
    conexion.close()

if __name__ == "__main__":
     crear_tablas()

    #insertar_categoria("Nómina", "Ingreso")
    #insertar_categoria("Alquiler", "Gasto")
    #insertar_categoria("Supermercado", "Gasto")
    #insertar_categoria("Coche", "Gasto")
    #insertar_categoria("Ocio", "Gasto")

    #insertar_movimiento("2026-09-01", "Cuenta Corriente", "Nómina", "Ingreso", 2200.00, None, "Sueldo septiembre")
    #insertar_movimiento("2026-09-03", "Cuenta Corriente", "Supermercado", "Gasto", 65.30, None, "")
    #insertar_movimiento("2026-09-04", "Cuenta Corriente", None, "Traspaso", 300.00, "Ahorro", "Ahorro mensual")

    #insertar_presupuesto("Alquiler", "09", 850.00)
    #insertar_presupuesto("Supermercado", "09", 300.00)
    #insertar_presupuesto("Ocio", "09", 150.00)

    #insertar_recurrente("Alquiler", "Cuenta Corriente", "Alquiler", "Gasto", 850.00, None, 1, "2026-09", 0)
    #insertar_recurrente("Cuota coche", "Cuenta Corriente", "Coche", "Gasto", 220.00, None, 5, "2026-09", 10)

     print("Datos migrados correctamente a la base de datos.")

     print("Recurrentes en la base de datos:")
     for r in obtener_recurrentes():
        print(r)

    #insertar_categoria("Nómina", "Ingreso")
    #insertar_categoria("Alquiler", "Gasto")
    #insertar_categoria("Supermercado", "Gasto")
    #insertar_categoria("Coche", "Gasto")
    #insertar_categoria("Ocio", "Gasto")

    #insertar_movimiento("2026-09-01", "Cuenta Corriente", "Nómina", "Ingreso", 2200.00, None, "Sueldo septiembre")
    #insertar_movimiento("2026-09-03", "Cuenta Corriente", "Supermercado", "Gasto", 65.30, None, "")
    #insertar_movimiento("2026-09-04", "Cuenta Corriente", None, "Traspaso", 300.00, "Ahorro", "Ahorro mensual")

    #insertar_presupuesto("Alquiler", "09", 850.00)
    #insertar_presupuesto("Supermercado", "09", 300.00)
    #insertar_presupuesto("Ocio", "09", 150.00)

    #insertar_recurrente("Alquiler", "Cuenta Corriente", "Alquiler", "Gasto", 850.00, None, 1, "2026-09", 0)
    #insertar_recurrente("Cuota coche", "Cuenta Corriente", "Coche", "Gasto", 220.00, None, 5, "2026-09", 10)

     print("Datos migrados correctamente a la base de datos.")

     print("Recurrentes en la base de datos:")
     for r in obtener_recurrentes():
        print(r)

def actualizar_cuenta(id_cuenta, nombre, banco, tipo, saldo_inicial):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE cuentas SET nombre = ?, banco = ?, tipo = ?, saldo_inicial = ? WHERE id = ?",
        (nombre, banco, tipo, saldo_inicial, id_cuenta)
    )
    conexion.commit()
    conexion.close()


def eliminar_cuenta(id_cuenta):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM cuentas WHERE id = ?", (id_cuenta,))
    conexion.commit()
    conexion.close()

def actualizar_categoria(id_categoria, nombre, tipo):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE categorias SET nombre = ?, tipo = ? WHERE id = ?",
        (nombre, tipo, id_categoria)
    )
    conexion.commit()
    conexion.close()


def eliminar_categoria(id_categoria):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM categoria WHERE id = ?", (id_categoria,))
    conexion.commit()
    conexion.close()

def actualizar_presupuesto(id_presupuesto, categoria, mes, presupuesto):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE presupuesto SET categoria = ?, mes = ?, presupuesto = ? WHERE id = ?",
        (categoria, mes, presupuesto, id_presupuesto)
    )
    conexion.commit()
    conexion.close()


def eliminar_presupuesto(id_presupuesto):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM presupuesto WHERE id = ?", (id_presupuesto,))
    conexion.commit()
    conexion.close()

def actualizar_recurrente(id_recurrente, descripcion, cuenta, categoria, tipo, importe, cuenta_destino, dia_del_mes, mes_inicio, cuotas_totales):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE recurrentes SET descripcion = ?, cuenta = ?, categoria = ?, tipo = ?, importe = ?, cuenta_destino = ?, dia_del_mes = ?, mes_inicio = ?, cuotas_totales = ? WHERE id = ?",
        (descripcion, cuenta, categoria, tipo, importe, cuenta_destino, dia_del_mes, mes_inicio, cuotas_totales, id_recurrente)
    )
    conexion.commit()
    conexion.close()


def eliminar_recurrente(id_recurrente):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM recurrentes WHERE id = ?", (id_recurrente,))
    conexion.commit()
    conexion.close()