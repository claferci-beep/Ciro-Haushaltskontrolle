import streamlit as st
from basedatos import obtener_movimientos, obtener_cuentas, actualizar_movimiento, eliminar_movimiento, obtener_categorias
from auth import verificar_password
verificar_password()

st.set_page_config(page_title="Movimientos", page_icon="📋", layout="wide")

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

    [data-testid="stFormSubmitButton"] button,
    [data-testid="stBaseButton-secondary"] {
    background-color: #35859E !important;
    border-color: #0F6B5C !important;
    }

    [data-testid="stFormSubmitButton"] button p {
    color: #FFFFFF !important;
    font-weight: bold !important;
    }

    [data-testid="stBaseButton-secondary"] p {
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
            Movimientos
        </div>
    </div>
""", unsafe_allow_html=True)

movimientos = obtener_movimientos()
cuentas = obtener_cuentas()
categorias = obtener_categorias()

nombres_cuentas = ["Todas"]
for c in cuentas:
    nombres_cuentas.append(c["nombre"])

nombres_categorias = []
for cat in categorias:
    nombres_categorias.append(cat["nombre"])

meses_disponibles = ["Todos"]
for mov in movimientos:
    mes = mov["fecha"][:7]
    if mes not in meses_disponibles:
        meses_disponibles.append(mes)

col1, col2 = st.columns(2)

col1.markdown('<p style="color:#FFFFFF; font-weight:bold; margin-bottom:0;">Filtrar por cuenta</p>', unsafe_allow_html=True)
cuenta_filtro = col1.selectbox("Filtrar por cuenta", nombres_cuentas, label_visibility="collapsed")

col2.markdown('<p style="color:#FFFFFF; font-weight:bold; margin-bottom:0;">Filtrar por mes</p>', unsafe_allow_html=True)
mes_filtro = col2.selectbox("Filtrar por mes", meses_disponibles, label_visibility="collapsed")

movimientos_filtrados = []
for mov in movimientos:
    coincide_cuenta = cuenta_filtro == "Todas" or mov["cuenta"] == cuenta_filtro
    coincide_mes = mes_filtro == "Todos" or mov["fecha"][:7] == mes_filtro
    if coincide_cuenta and coincide_mes:
        movimientos_filtrados.append(mov)

st.markdown(f'<p style="color:#FFFFFF; font-weight:bold;">Mostrando {len(movimientos_filtrados)} de {len(movimientos)} movimientos</p>', unsafe_allow_html=True)

meses_agrupados = {}
for mov in movimientos_filtrados:
    mes_mov = mov["fecha"][:7]
    if mes_mov not in meses_agrupados:
        meses_agrupados[mes_mov] = []
    meses_agrupados[mes_mov].append(mov)

meses_ordenados = sorted(meses_agrupados.keys(), reverse=True)

with st.container(height=280):
    for mes_mov in meses_ordenados:
        movs_del_mes = meses_agrupados[mes_mov]
        with st.expander(f"{mes_mov} ({len(movs_del_mes)})"):

            try:
                import pandas as pd

                df = pd.DataFrame(movs_del_mes)

                def color_fila(fila):
                    colores = {
                        "Gasto": "color: #C0392B; font-weight: bold; font-size: 1rem;",
                        "Ingreso": "color: #1F6FEB; font-weight: bold; font-size: 1rem;",
                        "Traspaso": "color: #0F6B5C;bold; font-size: 1rem;"
                    }
                    return [colores.get(fila["tipo"], "")] * len(fila)

                st.dataframe(
                    df.style.apply(color_fila, axis=1),
                    use_container_width=True,
                    column_config={
                        "nota": st.column_config.TextColumn("Nota", width="medium")
                    }
                )
            except Exception:
                colores_tipo = {"Gasto": "#C0392B", "Ingreso": "#1F6FEB", "Traspaso": "#0F6B5C"}
                filas_html = ""
                for mov in movs_del_mes:
                    color = colores_tipo.get(mov["tipo"], "#000000")
                    categoria = mov["categoria"] if mov["categoria"] else "-"
                    destino = mov["cuenta_destino"] if mov["cuenta_destino"] else "-"
                    nota = mov["nota"] if mov["nota"] else "-"
                    filas_html += f"""
                    <tr style="color: {color}; font-weight: bold; font-size: 0.95rem;">
                        <td style="padding:4px;">{mov['fecha']}</td>
                        <td style="padding:4px;">{mov['cuenta']}</td>
                        <td style="padding:4px;">{categoria}</td>
                        <td style="padding:4px;">{mov['tipo']}</td>
                        <td style="padding:4px;">{mov['importe']:.2f} €</td>
                        <td style="padding:4px;">{destino}</td>
                        <td style="padding:4px;">{nota}</td>
                    </tr>
                    """

                tabla_html = f"""
                <table style="width:100%; border-collapse: collapse; font-size: 0.85rem;">
                    <thead>
                        <tr style="background-color: #0F6B5C; color: white;">
                            <th style="padding:6px;">Fecha</th>
                            <th style="padding:6px;">Cuenta</th>
                            <th style="padding:6px;">Categoría</th>
                            <th style="padding:6px;">Tipo</th>
                            <th style="padding:6px;">Importe</th>
                            <th style="padding:6px;">Cuenta destino</th>
                            <th style="padding:6px;">Nota</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filas_html}
                    </tbody>
                </table>
                """
                st.markdown(tabla_html, unsafe_allow_html=True)

st.subheader("Editar o eliminar un movimiento")

if movimientos_filtrados:
    etiquetas = []
    for mov in movimientos_filtrados:
        etiquetas.append(f"{mov['fecha']} — {mov['cuenta']} — {mov['tipo']} — {mov['importe']:.2f} €")

    indice_elegido = st.selectbox("Elige un movimiento", range(len(etiquetas)), format_func=lambda i: etiquetas[i])
    mov = movimientos_filtrados[indice_elegido]

    colores_tipo = {"Gasto": "#AC270A", "Ingreso": "#153C96", "Traspaso": "#19C00D"}
    color_mov = colores_tipo.get(mov["tipo"], "#000000")
    st.markdown(    
        f"<p style='color:{color_mov}; font-weight:bold;'>Editando: {mov['fecha']} — {mov['cuenta']} — {mov['tipo']} — {mov['importe']:.2f} €</p>",
        unsafe_allow_html=True
    )

    nueva_fecha = st.text_input("Fecha (AAAA-MM-DD)", value=mov["fecha"])
    nueva_cuenta = st.selectbox("Cuenta", nombres_cuentas[1:], index=nombres_cuentas[1:].index(mov["cuenta"]) if mov["cuenta"] in nombres_cuentas[1:] else 0)
    nuevo_tipo = st.selectbox("Tipo", ["Ingreso", "Gasto", "Traspaso"], index=["Ingreso", "Gasto", "Traspaso"].index(mov["tipo"]))

    if nuevo_tipo == "Traspaso":
        opciones_destino = nombres_cuentas[1:]
        if mov["cuenta_destino"] and mov["cuenta_destino"] in opciones_destino:
            indice_destino = opciones_destino.index(mov["cuenta_destino"])
        else:
            indice_destino = 0
        nueva_cuenta_destino = st.selectbox("Cuenta destino", opciones_destino, index=indice_destino)
    else:
        nueva_cuenta_destino = None

    if mov["categoria"] and mov["categoria"] in nombres_categorias:
        indice_cat = nombres_categorias.index(mov["categoria"])
    else:
        indice_cat = 0
    nueva_categoria = st.selectbox("Categoría", nombres_categorias, index=indice_cat)

    nuevo_importe = st.number_input("Importe"),