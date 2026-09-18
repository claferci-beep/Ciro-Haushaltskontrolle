import streamlit as st
from basedatos import obtener_cuentas, obtener_movimientos, obtener_categorias, insertar_movimiento
from auth import verificar_password
verificar_password()

st.set_page_config(page_title="Nuevo", page_icon="➕")

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

    [data-testid="stSidebarNav"] a p,
    [data-testid="stSidebarNav"] a span {
        color: #0F6B5C !important;
    }

    [data-testid="stFormSubmitButton"] button,
    [data-testid="stBaseButton-secondary"] {
        background-color: #B8D5CF !important;
        border-color: #0F6B5C !important;
    }

    [data-testid="stFormSubmitButton"] button p {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }

    [data-testid="stSelectbox"] label p {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }

    [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }

    [data-testid="stDateInput"] label p {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }

    [data-testid="stNumberInput"] label p {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }

    [data-testid="stTextInput"] label p {
        color: #FFFFFF !important;
        font-weight: bold !important;
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
            Nuevo movimiento
        </div>
    </div>
""", unsafe_allow_html=True)

cuentas = obtener_cuentas()
movimientos = obtener_movimientos()
categorias = obtener_categorias()

nombres_cuentas = []
for cuenta in cuentas:
    nombres_cuentas.append(cuenta["nombre"])

st.subheader("Agregar nuevo movimiento")

tipo_movimiento = st.selectbox("Tipo", ["Ingreso", "Gasto", "Traspaso"], key="tipo_nuevo_mov")

if tipo_movimiento == "Traspaso":
    cuenta_destino_movimiento = st.selectbox("Cuenta destino", nombres_cuentas, key="destino_nuevo_mov")
else:
    cuenta_destino_movimiento = None

with st.form("nuevo_movimiento", clear_on_submit=True):
    fecha = st.date_input("Fecha")
    cuenta_movimiento = st.selectbox("Cuenta", nombres_cuentas)

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
        cuenta_destino_movimiento,
        nota_movimiento
    )
    st.success("Movimiento guardado correctamente.")
    st.rerun()