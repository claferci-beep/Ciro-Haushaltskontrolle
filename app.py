import streamlit as st
from basedatos import obtener_cuentas, obtener_movimientos, obtener_presupuesto, obtener_categorias, obtener_recurrentes, insertar_movimiento
from basedatos import crear_tablas
crear_tablas()

st.set_page_config(page_title="Dashboard", page_icon="🏠")

def contar_generados(descripcion, lista_movimientos):
    contador = 0
    for mov in lista_movimientos:
        if mov["nota"] == f"[Recurrente] {descripcion}":
            contador += 1
    return contador


def generar_recurrentes(lista_recurrentes, lista_movimientos, mes_actual):
    generados = []
    for r in lista_recurrentes:
        ya_generados = contar_generados(r["descripcion"], lista_movimientos)
        ya_existe_este_mes = False
        for mov in lista_movimientos:
            if mov["nota"] == f"[Recurrente] {r['descripcion']}" and mov["fecha"][:7] == mes_actual:
                ya_existe_este_mes = True

        cupo_disponible = r["cuotas_totales"] == 0 or ya_generados < r["cuotas_totales"]

        if not ya_existe_este_mes and cupo_disponible:
            fecha_nueva = f"{mes_actual}-{r['dia_del_mes']:02d}"
            insertar_movimiento(fecha_nueva, r["cuenta"], r["categoria"], r["tipo"], r["importe"], r["cuenta_destino"], f"[Recurrente] {r['descripcion']}")
            generados.append(r["descripcion"])
    return generados


def calcular_ingresos_gastos(lista_movimientos, mes):
    ingresos = 0
    gastos = 0
    for mov in lista_movimientos:
        if mov["fecha"][:7] == mes:
            if mov["tipo"] == "Ingreso":
                ingresos += mov["importe"]
            elif mov["tipo"] == "Gasto":
                gastos += mov["importe"]
    return ingresos, gastos


def calcular_real(categoria, mes, lista_movimientos):
    total = 0
    for mov in lista_movimientos:
        if mov["categoria"] == categoria and mov["fecha"][5:7] == mes and mov["tipo"] == "Gasto":
            total += mov["importe"]
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

categorias = obtener_categorias()
cuentas = obtener_cuentas()
movimientos = obtener_movimientos()
presupuestos = obtener_presupuesto()

for cuenta in cuentas:
    cuenta["saldo_actual"] = cuenta["saldo_inicial"]

aplicar_movimientos(cuentas, movimientos)

mes_actual = "2026-09"
ingresos, gastos = calcular_ingresos_gastos(movimientos, mes_actual)
balance = ingresos - gastos

st.title("Ciro Haushaltskontrolle")

st.subheader("Recurrentes del mes")
if st.button("Ejecutar recurrentes de este mes"):
    recurrentes = obtener_recurrentes()
    generados = generar_recurrentes(recurrentes, movimientos, mes_actual)
    if generados:
        st.success(f"Generados: {', '.join(generados)}")
    else:
        st.info("No hay recurrentes pendientes para este mes.")

saldo_total = 0
for cuenta in cuentas:
    saldo_total += cuenta["saldo_actual"]

st.metric("Saldo total", f"{saldo_total:.2f} €")

col1, col2, col3 = st.columns(3)
col1.metric("Ingresos del mes", f"{ingresos:.2f} €")
col2.metric("Gastos del mes", f"{gastos:.2f} €")
col3.metric("Balance del mes", f"{balance:.2f} €")

st.subheader("Mis cuentas")
for cuenta in cuentas:
    st.write(f"**{cuenta['nombre']}** ({cuenta['tipo']}) — {cuenta['saldo_actual']:.2f} €")

st.subheader("Consultar saldo de una cuenta")

nombres_cuentas = []
for cuenta in cuentas:
    nombres_cuentas.append(cuenta["nombre"])

cuenta_elegida = st.selectbox("Elige una cuenta:", nombres_cuentas)

for cuenta in cuentas:
    if cuenta["nombre"] == cuenta_elegida:
        st.write(f"Saldo de **{cuenta_elegida}**: {cuenta['saldo_actual']:.2f} €")

st.subheader("Presupuesto vs Real")

for item in presupuestos:
    real = calcular_real(item["categoria"], item["mes"], movimientos)
    if real > item["presupuesto"]:
        st.error(f"⚠️ {item['categoria']}: gastaste {real:.2f} € de {item['presupuesto']:.2f} € — excedido")
    else:
        st.success(f"✅ {item['categoria']}: gastaste {real:.2f} € de {item['presupuesto']:.2f} €")

st.subheader("Presupuesto vs Real (gráfico)")

for item in presupuestos:
    real = calcular_real(item["categoria"], item["mes"], movimientos)
    porcentaje = real / item["presupuesto"]

    if porcentaje > 1:
        porcentaje_mostrado = 1.0
    else:
        porcentaje_mostrado = porcentaje

    st.write(f"**{item['categoria']}**: {real:.2f} € de {item['presupuesto']:.2f} € ({porcentaje*100:.0f}%)")
    st.progress(porcentaje_mostrado)





st.subheader("Agregar nuevo movimiento")

with st.form("nuevo_movimiento"):
    fecha = st.date_input("Fecha")
    cuenta_movimiento = st.selectbox("Cuenta", nombres_cuentas)
    tipo_movimiento = st.selectbox("Tipo", ["Ingreso", "Gasto", "Traspaso"])

    nombres_categorias = []
    for cat in categorias:
        nombres_categorias.append(cat["nombre"])
    categoria_movimiento = st.selectbox("Categoría", nombres_categorias)

    importe_movimiento = st.number_input("Importe", min_value=0.0, step=0.01)
    nota_movimiento = st.text_input("Nota (opcional)")

    enviado = st.form_submit_button("Guardar movimiento")

if enviado:
    insertar_movimiento(
        str(fecha),
        cuenta_movimiento,
        categoria_movimiento,
        tipo_movimiento,
        importe_movimiento,
        None,
        nota_movimiento
    )
    st.success("Movimiento guardado correctamente. Refresca la página para ver los cambios reflejados.")