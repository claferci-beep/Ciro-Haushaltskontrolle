import streamlit as st
from basedatos import obtener_categorias, insertar_categoria, actualizar_categoria, eliminar_categoria
st.set_page_config(page_title="Categorias", page_icon="🏷️")

st.title("Categorias")

categorias = obtener_categorias()

st.subheader("categorias existentes")
for categoria in categorias:
    with st.expander(f"{categoria['nombre']} — {categoria['tipo']}"):
        nuevo_nombre = st.text_input("Nombre", value=categoria["nombre"], key=f"nombre_{categoria['id']}")
        nuevo_tipo = st.selectbox("Tipo", ["Ingreso", "Gasto"], key=f"tipo_{categoria['id']}")
        
        col1, col2 = st.columns(2)
        if col1.button("Guardar cambios", key=f"guardar_{categoria['id']}"):
            actualizar_categoria(categoria["id"], nuevo_nombre, nuevo_tipo)
            st.success("Actualizado. Refresca la página.")

        if col2.button("Eliminar categoria", key=f"eliminar_{categoria['id']}"):
            eliminar_categoria(categoria["id"])
            st.success("Eliminado. Refresca la página.")

st.subheader("Agregar nueva categoria")
with st.form("nueva_categoria"):
    nombre = st.text_input("Nombre")
    tipo = st.selectbox("Tipo", ["Ingreso", "Gasto"])
    enviado = st.form_submit_button("Agregar categoria")

if enviado:
    insertar_categoria(nombre, tipo)
    st.success("categoria agregada. Refresca la página.")
    