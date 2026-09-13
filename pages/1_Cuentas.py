import streamlit as st
from basedatos import obtener_cuentas, insertar_cuenta, actualizar_cuenta, eliminar_cuenta
st.set_page_config(page_title="Cuentas", page_icon="💰")
from auth import verificar_password
verificar_password()

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

cuentas = obtener_cuentas()

st.subheader("Cuentas existentes")
for cuenta in cuentas:
    with st.expander(f"{cuenta['nombre']} — {cuenta['saldo_actual']:.2f} €"):
        nuevo_nombre = st.text_input("Nombre", value=cuenta["nombre"], key=f"nombre_{cuenta['id']}")
        nuevo_banco = st.text_input("Banco", value=cuenta["banco"], key=f"banco_{cuenta['id']}")
        nuevo_tipo = st.selectbox("Tipo", ["Corriente", "Ahorro", "Efectivo"], key=f"tipo_{cuenta['id']}")
        nuevo_saldo = st.number_input("Saldo inicial", value=cuenta["saldo_inicial"], key=f"saldo_{cuenta['id']}")

        col1, col2 = st.columns(2)
        if col1.button("Guardar cambios", key=f"guardar_{cuenta['id']}"):
            actualizar_cuenta(cuenta["id"], nuevo_nombre, nuevo_banco, nuevo_tipo, nuevo_saldo)
            st.success("Actualizado. Refresca la página.")

        if col2.button("Eliminar cuenta", key=f"eliminar_{cuenta['id']}"):
            eliminar_cuenta(cuenta["id"])
            st.success("Eliminado. Refresca la página.")

st.subheader("Agregar nueva cuenta")
with st.form("nueva_cuenta"):
    nombre = st.text_input("Nombre")
    banco = st.text_input("Banco")
    tipo = st.selectbox("Tipo", ["Corriente", "Ahorro", "Efectivo"])
    saldo_inicial = st.number_input("Saldo inicial", min_value=0.0, step=0.01)
    enviado = st.form_submit_button("Agregar cuenta")

if enviado:
    insertar_cuenta(nombre, banco, tipo, saldo_inicial)
    st.success("Cuenta agregada. Refresca la página.")
