import streamlit as st
import plotly.graph_objects as go
from basedatos import obtener_movimientos, obtener_movimientos_archivo
from auth import verificar_password
verificar_password()

st.set_page_config(page_title="Resumen anual", page_icon="📊", layout="wide")

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

    [data-testid="stFormSubmitButton"] button p,
    [data-testid="stBaseButton-secondary"] p {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }



    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
    }

    [data-testid="stMetricLabel"] {
        color: #FFFFFF !important;
    }

    [data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebarNav"] a p,
    [data-testid="stSidebarNav"] a span {
        color: #0F6B5C !important;
    }

        .stApp h3 {
        color: #4BDFEB !important;
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
            Resumen anual
        </div>
    </div>
""", unsafe_allow_html=True)

movimientos_activos = obtener_movimientos()
movimientos_archivados = obtener_movimientos_archivo()

todos_los_movimientos = movimientos_activos + movimientos_archivados

anios_disponibles = []
for mov in todos_los_movimientos:
    anio_mov = mov["fecha"][:4]
    if anio_mov not in anios_disponibles:
        anios_disponibles.append(anio_mov)
anios_disponibles.sort(reverse=True)

if not anios_disponibles:
    st.info("Todavía no hay movimientos registrados.")
    st.stop()

anio_elegido = st.selectbox("Año", anios_disponibles)

movimientos_del_anio = []
for mov in todos_los_movimientos:
    if mov["fecha"][:4] == anio_elegido:
        movimientos_del_anio.append(mov)

resumen_mensual = {}
for mes_num in range(1, 13):
    mes_str = f"{anio_elegido}-{mes_num:02d}"
    resumen_mensual[mes_str] = {"ingresos": 0.0, "gastos": 0.0}

for mov in movimientos_del_anio:
    mes = mov["fecha"][:7]
    if mes not in resumen_mensual:
        continue
    if mov["tipo"] == "Ingreso":
        resumen_mensual[mes]["ingresos"] += mov["importe"]
    elif mov["tipo"] == "Gasto":
        resumen_mensual[mes]["gastos"] += mov["importe"]

meses_ordenados = sorted(resumen_mensual.keys())
ingresos_por_mes = [resumen_mensual[mes]["ingresos"] for mes in meses_ordenados]
gastos_por_mes = [resumen_mensual[mes]["gastos"] for mes in meses_ordenados]
ahorro_por_mes = [ingreso - gasto for ingreso, gasto in zip(ingresos_por_mes, gastos_por_mes)]

total_ingresos = sum(ingresos_por_mes)
total_gastos = sum(gastos_por_mes)
total_ahorro = total_ingresos - total_gastos

col1, col2, col3 = st.columns(3)
col1.metric("Ingresos del año", f"{total_ingresos:.2f} €")
col2.metric("Gastos del año", f"{total_gastos:.2f} €")
col3.metric("Ahorro del año", f"{total_ahorro:.2f} €")

st.subheader(f"Ingresos vs Gastos por mes — {anio_elegido}")

try:
    figura = go.Figure()
    figura.add_trace(go.Bar(name="Ingresos", x=meses_ordenados, y=ingresos_por_mes, marker_color="#0F6B5C"))
    figura.add_trace(go.Bar(name="Gastos", x=meses_ordenados, y=gastos_por_mes, marker_color="#C0524B"))
    figura.update_layout(barmode="group", height=350, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(figura, use_container_width=True)
except Exception:
    for i, mes in enumerate(meses_ordenados):
        st.write(f"{mes}: Ingresos {ingresos_por_mes[i]:.2f} € — Gastos {gastos_por_mes[i]:.2f} €")

st.subheader("Detalle por mes")

for i, mes in enumerate(meses_ordenados):
    st.write(f"**{mes}** — Ingresos: {ingresos_por_mes[i]:.2f} € | Gastos: {gastos_por_mes[i]:.2f} € | Ahorro: {ahorro_por_mes[i]:.2f} €")