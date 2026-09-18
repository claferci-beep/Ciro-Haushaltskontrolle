import streamlit as st
from basedatos import obtener_cuentas, insertar_cuenta, actualizar_cuenta, eliminar_cuenta, obtener_movimientos
from auth import verificar_password
verificar_password()

st.set_page_config(page_title="Cuentas", page_icon="💰")
from datetime import date

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
        border-left: 5px solid #0F6B5C;
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

    [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        color: #FFFFFF !important;
    }

    [data-testid="stSelectbox"] label {
        color: #FFFFFF !important;
    }

    
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p {
    color: #FFFFFF !important;

    }

    [data-testid="stExpander"] summary p {
        color: #FFFFFF !important;
        font-weight: bold !important;

    
   
    }


    [data-testid="stTextInput"] label p {
    color: #FFFFFF !important;
    
   }

    [data-testid="stNumberInput"] label p {
    color: #FFFFFF !important;
    }

    [data-testid="stFormSubmitButton"] button p {
    color: #FFFFFF !important;
    font-weight: bold !important;
    }


    [data-testid="stFormSubmitButton"] button,
    [data-testid="stBaseButton-secondary"] {
    background-color: #35859E !important;
    border-color: #0F6B5C !important;
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
            Cuentas
        </div>
    </div>
""", unsafe_allow_html=True)


def aplicar_movimientos(lista_cuentas, lista_movimientos):
    hoy = str(date.today())
    for mov in lista_movimientos:
        if mov["fecha"] > hoy:
            continue
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


cuentas = obtener_cuentas()
movimientos = obtener_movimientos()

for cuenta in cuentas:
    cuenta["saldo_actual"] = cuenta["saldo_inicial"]

aplicar_movimientos(cuentas, movimientos)

tipos_disponibles = ["Corriente", "Ahorro", "Efectivo", "Inversión", "Créditos"]

with st.expander(f"Cuentas existentes ({len(cuentas)})"):
    for cuenta in cuentas:
        with st.expander(f"{cuenta['nombre']} — {cuenta['saldo_actual']:.2f} € (inicial: {cuenta['saldo_inicial']:.2f} €)"):
            nuevo_nombre = st.text_input("Nombre", value=cuenta["nombre"], key=f"nombre_{cuenta['id']}")
            nuevo_banco = st.text_input("Banco", value=cuenta["banco"], key=f"banco_{cuenta['id']}")

            if cuenta["tipo"] in tipos_disponibles:
                indice_tipo = tipos_disponibles.index(cuenta["tipo"])
            else:
                indice_tipo = 0
            nuevo_tipo = st.selectbox("Tipo", tipos_disponibles, index=indice_tipo, key=f"tipo_{cuenta['id']}")

            nuevo_saldo = st.number_input("Saldo inicial", value=cuenta["saldo_inicial"], key=f"saldo_{cuenta['id']}")

            col1, col2 = st.columns(2)
            if col1.button("Guardar cambios", key=f"guardar_{cuenta['id']}"):
                actualizar_cuenta(cuenta["id"], nuevo_nombre, nuevo_banco, nuevo_tipo, nuevo_saldo)
                st.success("Actualizado.")
                st.rerun()

            if col2.button("Eliminar cuenta", key=f"eliminar_{cuenta['id']}"):
                eliminar_cuenta(cuenta["id"])
                st.success("Eliminado.")
                st.rerun()

st.subheader("Agregar nueva cuenta")
with st.form("nueva_cuenta", clear_on_submit=True):
    nombre = st.text_input("Nombre")
    banco = st.text_input("Banco")
    tipo = st.selectbox("Tipo", tipos_disponibles)
    saldo_inicial = st.number_input("Saldo inicial", step=0.01)
    enviado = st.form_submit_button("Agregar cuenta")

if enviado:
    insertar_cuenta(nombre, banco, tipo, saldo_inicial)
    st.success("Cuenta agregada.")
    st.rerun()