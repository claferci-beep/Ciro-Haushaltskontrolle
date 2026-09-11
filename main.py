from basedatos import obtener_cuentas, obtener_categorias, obtener_movimientos, obtener_presupuesto, obtener_recurrentes
from basedatos import obtener_cuentas, obtener_categorias, obtener_movimientos, obtener_presupuesto, obtener_recurrentes, insertar_movimiento

cuentas = obtener_cuentas()
categorias = obtener_categorias()
movimientos = obtener_movimientos()
presupuesto = obtener_presupuesto()
recurrentes = obtener_recurrentes()


def calcular_saldo_total(lista_cuentas):
    total = 0
    for cuenta in lista_cuentas:
        total = total + cuenta["saldo_inicial"]
    return total


def aplicar_movimientos(lista_cuentas, lista_movimientos):
    for mov in lista_movimientos:
        for cuenta in lista_cuentas:
            if cuenta["nombre"] == mov["cuenta"]:
                if mov["tipo"] == "Ingreso":
                    cuenta["saldo_actual"] += mov["importe"]
                elif mov["tipo"] == "Gasto":
                    cuenta["saldo_actual"] -= mov["importe"]
                elif mov["tipo"] == "Traspaso":
                    cuenta["saldo_actual"] -= mov["importe"]
            if cuenta["nombre"] == mov["cuenta_destino"]:
                cuenta["saldo_actual"] += mov["importe"]
    return lista_cuentas


def calcular_real(categoria, mes, lista_movimientos):
    total = 0
    for mov in lista_movimientos:
        if mov["categoria"] == categoria and mov["fecha"][5:7] == mes and mov["tipo"] == "Gasto":
            total += mov["importe"]
    return total


def contar_generados(descripcion, lista_movimientos):
    contador = 0
    for mov in lista_movimientos:
        if mov["nota"] == f"[Recurrente] {descripcion}":
            contador += 1
    return contador

def resumen_por_categoria(lista_movimientos, mes=None):
    resumen = {}
    for mov in lista_movimientos:
        if mes is not None and mov["fecha"][:7] != mes:
            continue
        clave = mov["categoria"]
        if clave is None:
            continue
        if clave not in resumen:
            resumen[clave] = 0
        resumen[clave] += mov["importe"]
    return resumen


def generar_recurrentes(lista_recurrentes, lista_movimientos, mes_actual):
    for r in lista_recurrentes:
        ya_generados = contar_generados(r["descripcion"], lista_movimientos)
        ya_existe_este_mes = False
        for mov in lista_movimientos:
            if mov["nota"] == f"[Recurrente] {r['descripcion']}" and mov["fecha"][:7] == mes_actual:
                ya_existe_este_mes = True

        cupo_disponible = r["cuotas_totales"] == 0 or ya_generados < r["cuotas_totales"]

        if not ya_existe_este_mes and cupo_disponible:
            nuevo_movimiento = {
                "fecha": f"{mes_actual}-{r['dia_del_mes']:02d}",
                "cuenta": r["cuenta"],
                "categoria": r["categoria"],
                "tipo": r["tipo"],
                "importe": r["importe"],
                "cuenta_destino": r["cuenta_destino"],
                "nota": f"[Recurrente] {r['descripcion']}"
            }
            lista_movimientos.append(nuevo_movimiento)
            insertar_movimiento(
                nuevo_movimiento["fecha"],
                nuevo_movimiento["cuenta"],
                nuevo_movimiento["categoria"],
                nuevo_movimiento["tipo"],
                nuevo_movimiento["importe"],
                nuevo_movimiento["cuenta_destino"],
                nuevo_movimiento["nota"]
            )
            print(f"Generado: {r['descripcion']} para {mes_actual}")
        else:
            print(f"Omitido: {r['descripcion']} (ya generado este mes o cuotas cumplidas)")

print("=== CATEGORÍAS ===")
for cat in categorias:
    print(f"{cat['nombre']} — {cat['tipo']}")

print("\n=== CUENTAS ===")
for cuenta in cuentas:
    print(f"{cuenta['nombre']} ({cuenta['tipo']}) — Saldo: {cuenta['saldo_inicial']} €")
print("\nSaldo total de todas las cuentas:", calcular_saldo_total(cuentas))

print("\n=== GENERANDO RECURRENTES DE SEPTIEMBRE ===")
generar_recurrentes(recurrentes, movimientos, "2026-09")

aplicar_movimientos(cuentas, movimientos)

print("\n=== SALDOS ACTUALIZADOS ===")
for cuenta in cuentas:
    print(f"{cuenta['nombre']}: {cuenta['saldo_actual']} €")

print("\n=== PRESUPUESTO vs REAL ===")
for item in presupuesto:
    real = calcular_real(item["categoria"], item["mes"], movimientos)
    diferencia = item["presupuesto"] - real
    print(f"{item['categoria']}: Presupuesto {item['presupuesto']} € | Real {real} € | Diferencia {diferencia} €")

print("\n=== RESUMEN POR CATEGORÍA (Septiembre 2026) ===")
resumen_sept = resumen_por_categoria(movimientos, "2026-09")
for categoria, total in resumen_sept.items():
    print(f"{categoria}: {total:.2f} €")


