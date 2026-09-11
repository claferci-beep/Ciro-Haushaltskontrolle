import streamlit as st
from basedatos import obtener_cuentas, insertar_cuenta, actualizar_cuenta, eliminar_cuenta
st.set_page_config(page_title="Cuentas", page_icon="💰")
from auth import verificar_password
verificar_password()

st.title("Cuentas")

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
