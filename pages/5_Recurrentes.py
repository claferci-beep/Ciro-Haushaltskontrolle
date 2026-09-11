import streamlit as st
from basedatos import obtener_recurrentes, insertar_recurrente, actualizar_recurrente, eliminar_recurrente, obtener_cuentas, obtener_categorias
st.set_page_config(page_title="Recurrentes", page_icon="🔁")
from auth import verificar_password
verificar_password()

st.title("Recurrentes")

recurrentes = obtener_recurrentes()
cuentas = obtener_cuentas()
categorias = obtener_categorias()

nombres_cuentas = []
for c in cuentas:
    nombres_cuentas.append(c["nombre"])

nombres_categorias = []
for cat in categorias:
    nombres_categorias.append(cat["nombre"])

st.subheader("Recurrentes existentes")
for r in recurrentes:
    with st.expander(f"{r['descripcion']} — {r['importe']:.2f} € (día {r['dia_del_mes']})"):
        nueva_descripcion = st.text_input("Descripción", value=r["descripcion"], key=f"desc_{r['id']}")
        nueva_cuenta = st.selectbox("Cuenta", nombres_cuentas, index=nombres_cuentas.index(r["cuenta"]) if r["cuenta"] in nombres_cuentas else 0, key=f"cuenta_{r['id']}")
        nueva_categoria = st.selectbox("Categoría", nombres_categorias, index=nombres_categorias.index(r["categoria"]) if r["categoria"] in nombres_categorias else 0, key=f"cat_{r['id']}")
        nuevo_tipo = st.selectbox("Tipo", ["Ingreso", "Gasto", "Traspaso"], index=["Ingreso", "Gasto", "Traspaso"].index(r["tipo"]), key=f"tipo_{r['id']}")
        nuevo_importe = st.number_input("Importe", value=r["importe"], key=f"importe_{r['id']}")
        nuevo_dia = st.number_input("Día del mes", value=r["dia_del_mes"], min_value=1, max_value=31, key=f"dia_{r['id']}")
        nuevas_cuotas = st.number_input("Cuotas totales (0 = indefinido)", value=r["cuotas_totales"], min_value=0, key=f"cuotas_{r['id']}")

        col1, col2 = st.columns(2)
        if col1.button("Guardar cambios", key=f"guardar_{r['id']}"):
            actualizar_recurrente(r["id"], nueva_descripcion, nueva_cuenta, nueva_categoria, nuevo_tipo, nuevo_importe, r["cuenta_destino"], nuevo_dia, r["mes_inicio"], nuevas_cuotas)
            st.success("Actualizado. Refresca la página.")

        if col2.button("Eliminar recurrente", key=f"eliminar_{r['id']}"):
            eliminar_recurrente(r["id"])
            st.success("Eliminado. Refresca la página.")

st.subheader("Agregar nuevo recurrente")
with st.form("nuevo_recurrente"):
    descripcion = st.text_input("Descripción")
    cuenta = st.selectbox("Cuenta", nombres_cuentas)
    categoria = st.selectbox("Categoría", nombres_categorias)
    tipo = st.selectbox("Tipo", ["Ingreso", "Gasto", "Traspaso"])
    importe = st.number_input("Importe", min_value=0.0, step=0.01)
    dia_del_mes = st.number_input("Día del mes", min_value=1, max_value=31, value=1)
    mes_inicio = st.text_input("Mes inicio (AAAA-MM)")
    cuotas_totales = st.number_input("Cuotas totales (0 = indefinido)", min_value=0, value=0)
    enviado = st.form_submit_button("Agregar recurrente")

if enviado:
    insertar_recurrente(descripcion, cuenta, categoria, tipo, importe, None, dia_del_mes, mes_inicio, cuotas_totales)
    st.success("Recurrente agregado. Refresca la página.")