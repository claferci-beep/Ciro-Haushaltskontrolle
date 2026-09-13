
import streamlit as st
from basedatos import obtener_movimientos, obtener_cuentas
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