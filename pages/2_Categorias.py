import streamlit as st
from basedatos import obtener_categorias, insertar_categoria, actualizar_categoria, eliminar_categoria
st.set_page_config(page_title="Categorias", page_icon="🏷️")
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

    [data-testid="stExpander"] summary p {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }

    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
    }

    [data-testid="stFormSubmitButton"] button p {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }

    [data-testid="stSelectbox"] label p {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }

    [data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }

    [data-testid="stSidebarNav"] a p,
    [data-testid="stSidebarNav"] a span {
        color: #0F6B5C !important;
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
            Categorias
        </div>
    </div>
""", unsafe_allow_html=True)

categorias = obtener_categorias()


with st.expander(f"Categorias existentes ({len(categorias)})"):
#st.subheader("categorias existentes")
 for categoria in categorias:
    with st.expander(f"{categoria['nombre']} — {categoria['tipo']}"):
        nuevo_nombre = st.text_input("Nombre", value=categoria["nombre"], key=f"nombre_{categoria['id']}")
        nuevo_tipo = st.selectbox("Tipo", ["Ingreso", "Gasto"], key=f"tipo_{categoria['id']}")
        
        col1, col2 = st.columns(2)
        if col1.button("Guardar cambios", key=f"guardar_{categoria['id']}"):
            actualizar_categoria(categoria["id"], nuevo_nombre, nuevo_tipo)
            st.success("Actualizado. Refresca la página.")
            st.rerun()

        if col2.button("Eliminar categoria", key=f"eliminar_{categoria['id']}"):
            eliminar_categoria(categoria["id"])
            st.success("Eliminado. Refresca la página.")
            st.rerun()

st.subheader("Agregar nueva categoria")
with st.form("nueva_categoria", clear_on_submit=True):
    nombre = st.text_input("Nombre")
    tipo = st.selectbox("Tipo", ["Ingreso", "Gasto"])
    enviado = st.form_submit_button("Agregar categoria")

if enviado:
    insertar_categoria(nombre, tipo)
    st.success("categoria agregada. Refresca la página.")
    st.rerun()

st.markdown("""
    <style>
    [data-testid="stSelectbox"] label p {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }

    [data-testid="stWidgetLabel"] p {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }

    [data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)
