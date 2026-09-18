import streamlit as st
import csv
import io
from datetime import date
from basedatos import obtener_movimientos, obtener_cuentas
from auth import verificar_password
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm

verificar_password()

st.set_page_config(page_title="Reportes", page_icon="📤")

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
            Generar Reportes
        </div>
    </div>
""", unsafe_allow_html=True)

movimientos = obtener_movimientos()
cuentas = obtener_cuentas()

nombres_cuentas = ["Todas"]
for c in cuentas:
    nombres_cuentas.append(c["nombre"])

st.subheader("Filtros")

col1, col2 = st.columns(2)
fecha_desde = col1.date_input("Desde", value=date(2026, 9, 1))
fecha_hasta = col2.date_input("Hasta", value=date.today())

cuenta_filtro = st.selectbox("Cuenta", nombres_cuentas)

movimientos_filtrados = []
for mov in movimientos:
    fecha_mov = date.fromisoformat(mov["fecha"])
    coincide_fecha = fecha_desde <= fecha_mov <= fecha_hasta
    coincide_cuenta = cuenta_filtro == "Todas" or mov["cuenta"] == cuenta_filtro
    if coincide_fecha and coincide_cuenta:
        movimientos_filtrados.append(mov)

st.subheader("Resumen del período")

total_ingresos = 0
total_gastos = 0
for mov in movimientos_filtrados:
    if mov["tipo"] == "Ingreso":
        total_ingresos += mov["importe"]
    elif mov["tipo"] == "Gasto":
        total_gastos += mov["importe"]

col1, col2, col3 = st.columns(3)
col1.metric("Movimientos encontrados", len(movimientos_filtrados))
col2.metric("Total ingresos", f"{total_ingresos:.2f} €")
col3.metric("Total gastos", f"{total_gastos:.2f} €")

with st.container(height=300):
    for mov in movimientos_filtrados:
        st.write(f"{mov['fecha']} | {mov['cuenta']} | {mov['tipo']} | {mov['importe']:.2f} €")

st.subheader("Descargar este reporte")

col1, col2 = st.columns(2)

# --- CSV ---
buffer_csv = io.StringIO()
escritor = csv.writer(buffer_csv)
escritor.writerow(["Fecha", "Cuenta", "Categoría", "Tipo", "Importe", "Cuenta destino", "Nota"])
for mov in movimientos_filtrados:
    escritor.writerow([
        mov["fecha"],
        mov["cuenta"],
        mov["categoria"] if mov["categoria"] else "",
        mov["tipo"],
        f"{mov['importe']:.2f}",
        mov["cuenta_destino"] if mov["cuenta_destino"] else "",
        mov["nota"] if mov["nota"] else ""
    ])

col1.download_button(
    label="Descargar CSV",
    data=buffer_csv.getvalue(),
    file_name=f"reporte_{fecha_desde}_{fecha_hasta}.csv",
    mime="text/csv"
)

# --- PDF ---
def generar_pdf_reporte(lista_movimientos, desde, hasta, cuenta, ingresos, gastos):
    buffer_pdf = io.BytesIO()
    doc = SimpleDocTemplate(buffer_pdf, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    estilos = getSampleStyleSheet()

    contenido = []
    contenido.append(Paragraph("Ciro Haushaltskontrolle — Reporte", estilos["Title"]))
    contenido.append(Paragraph(f"Período: {desde} a {hasta}", estilos["Normal"]))
    contenido.append(Paragraph(f"Cuenta: {cuenta}", estilos["Normal"]))
    contenido.append(Spacer(1, 6))
    contenido.append(Paragraph(f"Total ingresos: {ingresos:.2f} €  |  Total gastos: {gastos:.2f} €", estilos["Normal"]))
    contenido.append(Spacer(1, 14))

    datos_tabla = [["Fecha", "Cuenta", "Categoría", "Tipo", "Importe", "Nota"]]
    for mov in lista_movimientos:
        datos_tabla.append([
            mov["fecha"],
            mov["cuenta"],
            mov["categoria"] if mov["categoria"] else "-",
            mov["tipo"],
            f"{mov['importe']:.2f} €",
            mov["nota"] if mov["nota"] else "-"
        ])

    tabla = Table(datos_tabla, repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F6B5C")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#E4EEEC")]),
    ]))

    contenido.append(tabla)
    doc.build(contenido)
    buffer_pdf.seek(0)
    return buffer_pdf

pdf_bytes = generar_pdf_reporte(movimientos_filtrados, fecha_desde, fecha_hasta, cuenta_filtro, total_ingresos, total_gastos)

col2.download_button(
    label="Descargar PDF",
    data=pdf_bytes,
    file_name=f"reporte_{fecha_desde}_{fecha_hasta}.pdf",
    mime="application/pdf"
)