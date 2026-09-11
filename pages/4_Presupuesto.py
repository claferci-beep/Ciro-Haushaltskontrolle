import streamlit as st
from basedatos import obtener_presupuesto, insertar_presupuesto, actualizar_presupuesto, eliminar_presupuesto, obtener_categorias
st.set_page_config(page_title="Presupuesto", page_icon="📊")
from auth import verificar_password
verificar_password()

st.title("Presupuesto")

presupuestos = obtener_presupuesto()
categorias = obtener_categorias()

nombres_categorias = []
for cat in categorias:
    nombres_categorias.append(cat["nombre"])

st.subheader("Presupuestos existentes")
for item in presupuestos:
    with st.expander(f"{item['categoria']} — {item['mes']} — {item['presupuesto']:.2f} €"):
        nueva_categoria = st.selectbox("Categoría", nombres_categorias, index=nombres_categorias.index(item["categoria"]) if item["categoria"] in nombres_categorias else 0, key=f"cat_{item['id']}")
        nuevo_mes = st.text_input("Mes (formato MM)", value=item["mes"], key=f"mes_{item['id']}")
        nuevo_presupuesto = st.number_input("Presupuesto", value=item["presupuesto"], key=f"presu_{item['id']}")

        col1, col2 = st.columns(2)
        if col1.button("Guardar cambios", key=f"guardar_{item['id']}"):
            actualizar_presupuesto(item["id"], nueva_categoria, nuevo_mes, nuevo_presupuesto)
            st.success("Actualizado. Refresca la página.")

        if col2.button("Eliminar presupuesto", key=f"eliminar_{item['id']}"):
            eliminar_presupuesto(item["id"])
            st.success("Eliminado. Refresca la página.")

st.subheader("Agregar nuevo presupuesto")
with st.form("nuevo_presupuesto"):
    categoria = st.selectbox("Categoría", nombres_categorias)
    mes = st.text_input("Mes (formato MM)")
    presupuesto = st.number_input("Presupuesto", min_value=0.0, step=0.01)
    enviado = st.form_submit_button("Agregar presupuesto")

if enviado:
    insertar_presupuesto(categoria, mes, presupuesto)
    st.success("Presupuesto agregado. Refresca la página.")