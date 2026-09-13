import streamlit as st
from basedatos import obtener_presupuesto, insertar_presupuesto, actualizar_presupuesto, eliminar_presupuesto, obtener_categorias
st.set_page_config(page_title="Presupuesto", page_icon="📊")
from auth import verificar_password
verificar_password()

st.markdown("""
    <div style="
        background-color: #FFFFFF;
        border: 2px solid #0F6B5C;
        border-radius: 10px;
        padding: 14px 22px;
        margin-bottom: 18px;
    ">
        <div style="font-size: 1.5rem; font-weight: 700; color: #0F6B5C;">
            Presupuestos
        </div>
    </div>
""", unsafe_allow_html=True)

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