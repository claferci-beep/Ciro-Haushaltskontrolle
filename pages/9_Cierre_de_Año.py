import streamlit as st
from datetime import date
from basedatos import (
    obtener_movimientos, obtener_cuentas, actualizar_cuenta,
    eliminar_movimiento, insertar_movimiento_archivo, obtener_movimientos_archivo
)
from auth import verificar_password
verificar_password()

st.set_page_config(page_title="Cierre de año", page_icon="🔒")

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
            Cierre de año
        </div>
    </div>
""", unsafe_allow_html=True)

st.warning("Esta acción mueve los movimientos del año elegido a un archivo histórico y actualiza el saldo inicial de cada cuenta. No se puede deshacer.")

movimientos = obtener_movimientos()
cuentas = obtener_cuentas()

anios_disponibles = []
for mov in movimientos:
    anio_mov = mov["fecha"][:4]
    if anio_mov not in anios_disponibles:
        anios_disponibles.append(anio_mov)
anios_disponibles.sort()

if not anios_disponibles:
    st.info("No hay movimientos para archivar.")
    st.stop()

anio_elegido = st.selectbox("Año a cerrar", anios_disponibles)

movimientos_del_anio = []
for mov in movimientos:
    if mov["fecha"][:4] == anio_elegido:
        movimientos_del_anio.append(mov)

hoy = date.today()
fecha_limite = date(int(anio_elegido), 12, 31)
fecha_habilitada = hoy >= fecha_limite

st.write(f"Movimientos a archivar del año {anio_elegido}: **{len(movimientos_del_anio)}**")

if not fecha_habilitada:
    st.error(f"El cierre del año {anio_elegido} solo se puede realizar a partir del 31 de diciembre de {anio_elegido}.")
    st.stop()

st.subheader("Vista previa del saldo resultante por cuenta")

saldos_preview = {}
for cuenta in cuentas:
    saldos_preview[cuenta["nombre"]] = cuenta["saldo_inicial"]

for mov in movimientos_del_anio:
    if mov["cuenta"] in saldos_preview:
        if mov["tipo"] == "Ingreso":
            saldos_preview[mov["cuenta"]] += mov["importe"]
        elif mov["tipo"] in ("Gasto", "Traspaso"):
            saldos_preview[mov["cuenta"]] -= mov["importe"]
    if mov["cuenta_destino"] in saldos_preview:
        saldos_preview[mov["cuenta_destino"]] += mov["importe"]

for nombre, saldo in saldos_preview.items():
    st.write(f"{nombre}: {saldo:.2f} €")

st.subheader("Confirmar cierre")

clave_ingresada = st.text_input("Ingresa la contraseña para confirmar", type="password")

if st.button("Ejecutar cierre de año"):
    if clave_ingresada != st.secrets["password"]:
        st.error("Contraseña incorrecta. El cierre no se ejecutó.")
    else:
        for mov in movimientos_del_anio:
            insertar_movimiento_archivo(
                anio_elegido, mov["fecha"], mov["cuenta"], mov["categoria"],
                mov["tipo"], mov["importe"], mov["cuenta_destino"], mov["nota"]
            )
            eliminar_movimiento(mov["id"])

        for cuenta in cuentas:
            nuevo_saldo = saldos_preview[cuenta["nombre"]]
            actualizar_cuenta(cuenta["id"], cuenta["nombre"], cuenta["banco"], cuenta["tipo"], nuevo_saldo)

        st.success(f"Año {anio_elegido} cerrado correctamente. {len(movimientos_del_anio)} movimientos archivados.")
        st.rerun()

st.subheader("Consultar archivo histórico")

anios_archivados = []
todos_archivados = obtener_movimientos_archivo()
for mov in todos_archivados:
    if mov["anio"] not in anios_archivados:
        anios_archivados.append(mov["anio"])
anios_archivados.sort(reverse=True)

if anios_archivados:
    anio_consulta = st.selectbox("Ver año archivado", anios_archivados)
    movimientos_archivo_anio = obtener_movimientos_archivo(anio_consulta)
    with st.container(height=300):
        st.dataframe(movimientos_archivo_anio, use_container_width=True)
else:
    st.write("Todavía no hay años archivados.")