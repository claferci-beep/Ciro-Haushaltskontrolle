
import streamlit as st
from basedatos import obtener_movimientos, obtener_cuentas

st.set_page_config(page_title="Movimientos", page_icon="📋")

st.title("Movimientos")

movimientos = obtener_movimientos()
cuentas = obtener_cuentas()

nombres_cuentas = ["Todas"]
for c in cuentas:
    nombres_cuentas.append(c["nombre"])

meses_disponibles = ["Todos"]
for mov in movimientos:
    mes = mov["fecha"][:7]
    if mes not in meses_disponibles:
        meses_disponibles.append(mes)

col1, col2 = st.columns(2)
cuenta_filtro = col1.selectbox("Filtrar por cuenta", nombres_cuentas)
mes_filtro = col2.selectbox("Filtrar por mes", meses_disponibles)

movimientos_filtrados = []
for mov in movimientos:
    coincide_cuenta = cuenta_filtro == "Todas" or mov["cuenta"] == cuenta_filtro
    coincide_mes = mes_filtro == "Todos" or mov["fecha"][:7] == mes_filtro
    if coincide_cuenta and coincide_mes:
        movimientos_filtrados.append(mov)

st.write(f"Mostrando {len(movimientos_filtrados)} de {len(movimientos)} movimientos")
tabla_md = "| Fecha | Cuenta | Categoría | Tipo | Importe | Cuenta destino | Nota |\n"
tabla_md += "|---|---|---|---|---|---|---|\n"

for mov in movimientos_filtrados:
    categoria = mov["categoria"] if mov["categoria"] else "-"
    destino = mov["cuenta_destino"] if mov["cuenta_destino"] else "-"
    nota = mov["nota"] if mov["nota"] else "-"
    tabla_md += f"| {mov['fecha']} | {mov['cuenta']} | {categoria} | {mov['tipo']} | {mov['importe']:.2f} € | {destino} | {nota} |\n"

with st.container(height=400):
    st.markdown(tabla_md)