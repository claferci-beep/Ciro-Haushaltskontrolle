import streamlit as st
from basedatos import obtener_movimientos, obtener_cuentas, actualizar_movimiento, eliminar_movimiento, obtener_categorias
from auth import verificar_password
verificar_password()

st.set_page_config(page_title="Movimientos", page_icon="📋")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    [data-testid="stMarkdownContainer"],
    [data-testid="stMetricValue"],
    [data-testid="stMetricLabel"],
    [data-testid="stWidgetLabel"],
    .stApp h1, .stApp h2, .stApp h3,
    .stApp p, .stApp label {
        font-family: 'Inter', sans-serif !important;
    }

    [data-testid="stMetric"] {
        background-color: #E4EEEC;
        border-left: 5px solid #0F6B5C;
        border-radius: 8px;
        padding: 14px 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }

    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
    }

    [data-testid="stSidebar"] {
        background-color: #B8D5CF;
    }

    [data-testid="stSidebarNav"] a {
        background-color: #FFFFFF;
        border: 2px solid #0F6B5C;
        border-radius: 10px;
        margin: 6px 10px;
        padding: 10px 14px;
        color: #0F6B5C !important;
        font-weight: 600;
        display: block;
    }

    [data-testid="stSidebarNav"] a:hover {
        background-color: #A5C7C0;
    }

    [data-testid="stMarkdownContainer"] h3 {
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div style="
        background-color: #FFFFFF;
        border: 2px solid #0F6B5C;
        border-radius: 10px;
        padding: 14px 22px;
        margin-bottom: 18px;
    ">
        <div style="font-size: 1.5rem; font-weight: 700; color: #0F6B5C;">
            Movimientos
        </div>
    </div>
""", unsafe_allow_html=True)

movimientos = obtener_movimientos()
cuentas = obtener_cuentas()
categorias = obtener_categorias()

nombres_cuentas = ["Todas"]
for c in cuentas:
    nombres_cuentas.append(c["nombre"])

nombres_categorias = []
for cat in categorias:
    nombres_categorias.append(cat["nombre"])

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

try:
    st.dataframe(movimientos_filtrados, use_container_width=True)
except Exception:
    tabla_md = "| Fecha | Cuenta | Categoría | Tipo | Importe | Cuenta destino | Nota |\n"
    tabla_md += "|---|---|---|---|---|---|---|\n"

    for mov in movimientos_filtrados:
        categoria = mov["categoria"] if mov["categoria"] else "-"
        destino = mov["cuenta_destino"] if mov["cuenta_destino"] else "-"
        nota = mov["nota"] if mov["nota"] else "-"
        tabla_md += f"| {mov['fecha']} | {mov['cuenta']} | {categoria} | {mov['tipo']} | {mov['importe']:.2f} € | {destino} | {nota} |\n"

    with st.container(height=400):
        st.markdown(tabla_md)

st.subheader("Editar o eliminar un movimiento")

if movimientos_filtrados:
    etiquetas = []
    for mov in movimientos_filtrados:
        etiquetas.append(f"{mov['fecha']} — {mov['cuenta']} — {mov['tipo']} — {mov['importe']:.2f} €")

    indice_elegido = st.selectbox("Elige un movimiento", range(len(etiquetas)), format_func=lambda i: etiquetas[i])
    mov = movimientos_filtrados[indice_elegido]

    nueva_fecha = st.text_input("Fecha (AAAA-MM-DD)", value=mov["fecha"])
    nueva_cuenta = st.selectbox("Cuenta", nombres_cuentas[1:], index=nombres_cuentas[1:].index(mov["cuenta"]) if mov["cuenta"] in nombres_cuentas[1:] else 0)
    nuevo_tipo = st.selectbox("Tipo", ["Ingreso", "Gasto", "Traspaso"], index=["Ingreso", "Gasto", "Traspaso"].index(mov["tipo"]))

    if nuevo_tipo == "Traspaso":
        opciones_destino = nombres_cuentas[1:]
        if mov["cuenta_destino"] and mov["cuenta_destino"] in opciones_destino:
            indice_destino = opciones_destino.index(mov["cuenta_destino"])
        else:
            indice_destino = 0
        nueva_cuenta_destino = st.selectbox("Cuenta destino", opciones_destino, index=indice_destino)
    else:
        nueva_cuenta_destino = None

    if mov["categoria"] and mov["categoria"] in nombres_categorias:
        indice_cat = nombres_categorias.index(mov["categoria"])
    else:
        indice_cat = 0
    nueva_categoria = st.selectbox("Categoría", nombres_categorias, index=indice_cat)

    nuevo_importe = st.number_input("Importe", value=mov["importe"])
    nueva_nota = st.text_input("Nota", value=mov["nota"] if mov["nota"] else "")

    colA, colB = st.columns(2)
    if colA.button("Guardar cambios"):
        actualizar_movimiento(mov["id"], nueva_fecha, nueva_cuenta, nueva_categoria, nuevo_tipo, nuevo_importe, nueva_cuenta_destino, nueva_nota)
        st.success("Actualizado.")
        st.rerun()

    if colB.button("Eliminar movimiento"):
        eliminar_movimiento(mov["id"])
        st.success("Eliminado.")
        st.rerun()
else:
    st.info("No hay movimientos para editar con los filtros actuales.")