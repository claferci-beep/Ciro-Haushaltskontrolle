import calendar
import re
import pandas as pd
import numbers
from datetime import date

from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

import streamlit as st

from basedatos import (obtener_recurrentes, obtener_movimientos, obtener_cuentas, obtener_categorias,
                       crear_tabla_planificacion, obtener_plan_mes, guardar_plan_mes,
                       crear_tabla_plan_items, obtener_plan_items, insertar_plan_item,
                       actualizar_plan_item, vincular_plan_item, eliminar_plan_item,
                       insertar_movimiento, actualizar_movimiento, obtener_ultimo_movimiento_id)

from confirmacion import confirmar, mostrar_aviso

st.set_page_config(page_title="Planificación", page_icon="🗓️", layout="wide")
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
            Planificación
        </div>
    </div>
""", unsafe_allow_html=True)

mostrar_aviso()
crear_tabla_planificacion()
crear_tabla_plan_items()

CUENTA_PRINCIPAL = "01 - Girokonto"


def sumar_meses(mes_texto, n):
    anio, mes = int(mes_texto[:4]), int(mes_texto[5:7])
    total = anio * 12 + (mes - 1) + n
    return f"{total // 12}-{total % 12 + 1:02d}"


def diferencia_meses(desde, hasta):
    return (int(hasta[:4]) - int(desde[:4])) * 12 + int(hasta[5:7]) - int(desde[5:7])


def planificar_recurrentes(lista_recurrentes, lista_movimientos, mes):
    hoy = str(date.today())


    mes_hoy = hoy[:7]
    anio, num_mes = int(mes[:4]), int(mes[5:7])
    ultimo_dia = calendar.monthrange(anio, num_mes)[1]
    filas = []

    for r in lista_recurrentes:
        inicio = (r["mes_inicio"] or "").strip()
        if len(inicio) == 7 and mes < inicio:
            continue

        nota = f"[Recurrente] {r['descripcion']}"
        generados = sorted(m["fecha"] for m in lista_movimientos if m["nota"] == nota)
        real = next((m for m in lista_movimientos if m["nota"] == nota and m["fecha"][:7] == mes), None)
        total_cuotas = int(r["cuotas_totales"] or 0)
        previas = int(r.get("cuotas_previas") or 0)

        if real:
            fecha = real["fecha"]
            importe = float(real["importe"])
            numero_cuota = generados.index(real["fecha"]) + 1 + previas
            estado = "✅ Pagado" if fecha <= hoy else "⏳ Registrado"
        else:
            fecha = f"{mes}-{min(int(r['dia_del_mes']), ultimo_dia):02d}"
            importe = float(r["importe"])
            if generados:
                numero_cuota = max(1, len(generados) + diferencia_meses(generados[-1][:7], mes)) + previas
            else:
                numero_cuota = 1 + previas
            if total_cuotas and numero_cuota > total_cuotas:
                continue
            if fecha <= hoy and mes <= mes_hoy:
                estado = "⚠️ Sin generar"
            else:
                estado = "📅 Previsto"

        filas.append({
            "Fecha": fecha,
            "Concepto": r["descripcion"],
            "Cuenta": r["cuenta"],
            "Tipo": r["tipo"],
            "Importe": importe,
            "Cuota": f"{numero_cuota} / {total_cuotas}" if total_cuotas else "—",
            "Estado": estado,
        })

    return sorted(filas, key=lambda f: f["Fecha"])

def saldo_actual_cuenta(nombre, lista_cuentas, lista_movimientos):
    hoy = str(date.today())
    cuenta = next((c for c in lista_cuentas if c["nombre"] == nombre), None)
    if not cuenta:
        return 0.0
    saldo = float(cuenta["saldo_inicial"])
    for m in lista_movimientos:
        if m["fecha"] > hoy:
            continue
        importe = float(m["importe"])
        if m["cuenta"] == nombre:
            saldo += importe if m["tipo"] == "Ingreso" else -importe
        if m["cuenta_destino"] == nombre:
            saldo += importe
    return saldo

def es_numero(valor):
    return isinstance(valor, numbers.Number) and valor == valor


def num(valor):
    return float(valor) if es_numero(valor) else 0.0

def texto(valor):
    if valor is None:
        return None
    try:
        if pd.isna(valor):
            return None
    except (TypeError, ValueError):
        pass
    return str(valor)


def preparar_tabla(datos, columnas_texto):
    df = pd.DataFrame(datos)
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    for columna in columnas_texto:
        df[columna] = df[columna].astype("string")
    return df


def a_fecha(texto):
    try:
        return date.fromisoformat(str(texto)[:10]) if texto else None
    except ValueError:
        return None


def a_texto_fecha(valor):
    texto = str(valor)[:10] if valor is not None else ""
    return texto if re.fullmatch(r"\d{4}-\d{2}-\d{2}", texto) else None


def a_filas(resultado):
    if hasattr(resultado, "to_dict"):
        return resultado.to_dict("records")
    if isinstance(resultado, dict):
        columnas = list(resultado.keys())
        if not columnas:
            return []
        primera = resultado[columnas[0]]
        indices = list(primera.keys()) if isinstance(primera, dict) else range(len(primera))
        return [{c: resultado[c][i] for c in columnas} for i in indices]
    return list(resultado)


def estado_item(item, ids_movimientos, hoy):
    mov_id = item.get("movimiento_id")
    if es_numero(mov_id) and int(mov_id) in ids_movimientos:
        return "✅ Pagado" if (item.get("fecha") or "") <= hoy else "⏳ Registrado"
    return "📝 Planificado"


def pendiente_de_restar(fecha_texto, fecha_corte):
    return not fecha_texto or fecha_texto > fecha_corte


def sincronizar(mes, grupo, filas_editadas, items_db, ids_movimientos):
    items_por_id = {int(i["id"]): i for i in items_db if es_numero(i.get("id"))}
    ids_vistos = set()
    for f in filas_editadas:
        fecha_txt = a_texto_fecha(f.get("Fecha"))
        importe = num(f.get("Importe"))
        concepto = texto(f.get("Concepto")) or ("Ahorro" if grupo == "Ahorro" else "")
        cuenta = texto(f.get("Cuenta")) or CUENTA_PRINCIPAL
        destino = texto(f.get("Cuenta destino"))
        categoria = texto(f.get("Categoría"))

        if es_numero(f.get("id")):
            id_item = int(f["id"])
            ids_vistos.add(id_item)
            actualizar_plan_item(id_item, concepto, fecha_txt, cuenta, destino, categoria, importe)
            mov_id = items_por_id.get(id_item, {}).get("movimiento_id")
            if es_numero(mov_id) and int(mov_id) in ids_movimientos and fecha_txt and importe > 0:
                tipo = "Traspaso" if grupo == "Ahorro" else "Gasto"
                actualizar_movimiento(int(mov_id), fecha_txt, cuenta, categoria, tipo, importe, destino, f"[Plan] {concepto}")
        elif concepto or importe > 0:
            insertar_plan_item(mes, grupo, concepto, fecha_txt, cuenta, destino, categoria, importe)

    for id_item in items_por_id:
        if id_item not in ids_vistos:
            eliminar_plan_item(id_item)


def registrar_planificacion(mes, ids_movimientos):
    for grupo in ("Pago", "Ahorro"):
        for it in obtener_plan_items(mes, grupo):
            ya_registrado = es_numero(it.get("movimiento_id")) and int(it["movimiento_id"]) in ids_movimientos
            if ya_registrado or not it["fecha"] or num(it["importe"]) <= 0:
                continue
            tipo = "Traspaso" if grupo == "Ahorro" else "Gasto"
            nota = f"[Plan] {it['descripcion']}"
            insertar_movimiento(it["fecha"], it["cuenta"], it["categoria"], tipo, it["importe"], it["cuenta_destino"], nota)
            vincular_plan_item(int(it["id"]), obtener_ultimo_movimiento_id(nota, it["fecha"]))


PDF_PETROL = colors.HexColor("#0F6B5C")
PDF_FONDO = colors.HexColor("#E4EEEC")


def euros(valor):
    return f"{valor:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def sin_icono(estado):
    return estado.split(" ", 1)[1] if estado and " " in estado else (estado or "")


def fecha_de(valor):
    t = a_texto_fecha(valor)
    return f"{t[8:10]}.{t[5:7]}.{t[:4]}" if t else "—"


def tabla_pdf(encabezados, filas_tabla, anchos, columna_importe):
    tabla = Table([encabezados] + filas_tabla, colWidths=anchos, repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PDF_PETROL),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PDF_FONDO]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#B8D5CF")),
        ("ALIGN", (columna_importe, 1), (columna_importe, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return tabla


def generar_pdf(mes, resumen, texto_saldo, fijos, variables, ahorro):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title=f"Planificación {mes}",
                            leftMargin=1.5 * cm, rightMargin=1.5 * cm,
                            topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    estilos = getSampleStyleSheet()
    estilos["Title"].textColor = PDF_PETROL
    estilos["Heading2"].textColor = PDF_PETROL

    elementos = [
        Paragraph(f"Planificación {mes}", estilos["Title"]),
        Paragraph(f"CIRO Haushaltskontrolle · generado el {date.today().strftime('%d.%m.%Y')}", estilos["Normal"]),
        Spacer(1, 0.4 * cm),
        Paragraph("Resumen", estilos["Heading2"]),
        tabla_pdf(["Concepto", "Importe"], [[c, euros(v)] for c, v in resumen], [11 * cm, 5 * cm], 1),
        Paragraph(texto_saldo, estilos["Italic"]),
    ]

    if fijos:
        elementos += [Spacer(1, 0.4 * cm), Paragraph("Pagos fijos", estilos["Heading2"]),
                      tabla_pdf(["Fecha", "Concepto", "Cuenta", "Cuota", "Estado", "Importe"], fijos,
                                [2.2 * cm, 4.6 * cm, 4 * cm, 1.8 * cm, 2.6 * cm, 2.6 * cm], 5)]
    if variables:
        elementos += [Spacer(1, 0.4 * cm), Paragraph("Pagos variables y puntuales", estilos["Heading2"]),
                      tabla_pdf(["Fecha", "Concepto", "Cuenta", "Categoría", "Estado", "Importe"], variables,
                                [2.2 * cm, 4 * cm, 3.6 * cm, 3 * cm, 2.4 * cm, 2.6 * cm], 5)]
    if ahorro:
        elementos += [Spacer(1, 0.4 * cm), Paragraph("Ahorro del mes", estilos["Heading2"]),
                      tabla_pdf(["Cuenta destino", "Fecha", "Estado", "Importe"], ahorro,
                                [7 * cm, 3 * cm, 3.4 * cm, 3 * cm], 3)]

    doc.build(elementos)
    return buffer.getvalue()

mes_hoy = date.today().strftime("%Y-%m")
opciones_mes = [sumar_meses(mes_hoy, n) for n in (-1, 0, 1, 2)]

col_mes, _ = st.columns([1, 3])
mes_elegido = col_mes.selectbox("Mes a planificar", opciones_mes, index=1)

movimientos = obtener_movimientos()
filas = planificar_recurrentes(obtener_recurrentes(), movimientos, mes_elegido)

plan = obtener_plan_mes(mes_elegido)
saldo_hoy_giro = saldo_actual_cuenta(CUENTA_PRINCIPAL, obtener_cuentas(), movimientos)

if plan and plan["saldo_partida"] is not None:
    saldo_partida = float(plan["saldo_partida"])
    fecha_corte = plan["fecha_saldo"]
    texto_saldo = f"📌 Fijado el {fecha_corte}"
else:
    saldo_partida = saldo_hoy_giro
    fecha_corte = str(date.today())
    texto_saldo = "Provisional: saldo actual de Girokonto"

otros_guardados = float(plan["otros_ingresos"]) if plan else 0.0

st.subheader("Resumen del mes")

col_otros, col_btn = st.columns([1, 1])
otros_ingresos = col_otros.number_input(
    "Sonst. Plus (otros ingresos)", value=otros_guardados,
    min_value=0.0, step=0.01, format="%.2f", key=f"otros_{mes_elegido}"
)

saldo_guardado = plan["saldo_partida"] if plan else None
fecha_guardada = plan["fecha_saldo"] if plan else None

col_btn.write("")
if col_btn.button("💾 Guardar Sonst. Plus"):
    guardar_plan_mes(mes_elegido, saldo_guardado, fecha_guardada, otros_ingresos)
    st.session_state["_aviso"] = "Sonst. Plus guardado."
    st.rerun()

col_fijar, col_soltar = st.columns(2)
if col_fijar.button(f"📌 Fijar saldo de partida ({saldo_hoy_giro:.2f} €)", width="stretch"):
    confirmar(
        f"¿Fijar {saldo_hoy_giro:.2f} € como saldo de partida de {mes_elegido}?",
        guardar_plan_mes, mes_elegido, saldo_hoy_giro, str(date.today()), otros_guardados
    )
if plan and plan["saldo_partida"] is not None:
    if col_soltar.button("↩️ Volver a saldo provisional", width="stretch"):
        confirmar(
            f"¿Quitar el saldo fijado de {mes_elegido} y volver al saldo actual?",
            guardar_plan_mes, mes_elegido, None, None, otros_guardados
        )

cargos_giro = [f for f in filas if f["Cuenta"] == CUENTA_PRINCIPAL and f["Tipo"] in ("Gasto", "Traspaso")]
cargos_restantes = sum(f["Importe"] for f in cargos_giro if f["Fecha"] > fecha_corte)

contenedor_resumen = st.container()

hoy_txt = str(date.today())
ids_movimientos = {int(m["id"]) for m in movimientos}
nombres_cuentas = [c["nombre"] for c in obtener_cuentas()]
nombres_categorias = [c["nombre"] for c in obtener_categorias()]
cuentas_ahorro = [n for prefijo in ("05", "03", "04") for n in nombres_cuentas if n.startswith(prefijo)]

# ---------- Pagos variables y puntuales ----------
st.subheader("Pagos variables y puntuales")
items_pagos = obtener_plan_items(mes_elegido, "Pago")

if not items_pagos:
    mes_anterior = sumar_meses(mes_elegido, -1)
    anteriores = obtener_plan_items(mes_anterior, "Pago")
    if anteriores and st.button(f"📋 Copiar posiciones de {mes_anterior}"):
        for a in anteriores:
            insertar_plan_item(mes_elegido, "Pago", a["descripcion"], None, a["cuenta"], None, a["categoria"], 0)
        st.rerun()

datos_pagos = {
    "id": [p["id"] for p in items_pagos],
    "Fecha": [a_fecha(p["fecha"]) for p in items_pagos],
    "Concepto": [p["descripcion"] for p in items_pagos],
    "Cuenta": [p["cuenta"] for p in items_pagos],
    "Categoría": [p["categoria"] for p in items_pagos],
    "Importe": [num(p["importe"]) for p in items_pagos],
    "Estado": [estado_item(p, ids_movimientos, hoy_txt) for p in items_pagos],
}

editado_pagos = st.data_editor(
    preparar_tabla(datos_pagos, ["Concepto", "Cuenta", "Categoría", "Estado"]),
    key=f"editor_pagos_{mes_elegido}",
    num_rows="dynamic",
    hide_index=True,
    width="stretch",
    disabled=["Estado"],
    column_config={
        "id": None,
        "Fecha": st.column_config.DateColumn("Fecha", format="DD.MM.YYYY"),
        "Concepto": st.column_config.TextColumn("Concepto"),
        "Cuenta": st.column_config.SelectboxColumn("Cuenta", options=nombres_cuentas, default=CUENTA_PRINCIPAL),
        "Categoría": st.column_config.SelectboxColumn("Categoría", options=nombres_categorias),
        "Importe": st.column_config.NumberColumn("Importe", min_value=0.0, step=0.01, format="%.2f €", default=0.0),
        "Estado": st.column_config.TextColumn("Estado"),
    },
)

# ---------- Ahorro del mes ----------
st.subheader("Ahorro del mes")
items_ahorro = obtener_plan_items(mes_elegido, "Ahorro")
if not items_ahorro:
    items_ahorro = [{"id": None, "fecha": None, "descripcion": "Ahorro", "cuenta": CUENTA_PRINCIPAL,
                     "cuenta_destino": c, "categoria": None, "importe": 0, "movimiento_id": None}
                    for c in cuentas_ahorro]

datos_ahorro = {
    "id": [a["id"] for a in items_ahorro],
    "Cuenta destino": [a["cuenta_destino"] for a in items_ahorro],
    "Fecha": [a_fecha(a["fecha"]) for a in items_ahorro],
    "Importe": [num(a["importe"]) for a in items_ahorro],
    "Estado": [estado_item(a, ids_movimientos, hoy_txt) for a in items_ahorro],
}

editado_ahorro = st.data_editor(
    preparar_tabla(datos_ahorro, ["Cuenta destino", "Estado"]),
    key=f"editor_ahorro_{mes_elegido}",
    hide_index=True,
    width="stretch",
    disabled=["Cuenta destino", "Estado"],
    column_config={
        "id": None,
        "Fecha": st.column_config.DateColumn("Fecha", format="DD.MM.YYYY"),
        "Importe": st.column_config.NumberColumn("Importe", min_value=0.0, step=0.01, format="%.2f €"),
    },
)

filas_pagos = a_filas(editado_pagos)
filas_ahorro = a_filas(editado_ahorro)

col_guardar, col_registrar = st.columns(2)
if col_guardar.button("💾 Guardar planificación", type="primary", width="stretch"):
    sincronizar(mes_elegido, "Pago", filas_pagos, obtener_plan_items(mes_elegido, "Pago"), ids_movimientos)
    sincronizar(mes_elegido, "Ahorro", filas_ahorro, obtener_plan_items(mes_elegido, "Ahorro"), ids_movimientos)
    st.session_state["_aviso"] = "Planificación guardada."
    st.rerun()

if col_registrar.button("📤 Registrar en Movimientos", width="stretch"):
    confirmar(
        f"¿Registrar en Movimientos las posiciones de {mes_elegido} con fecha e importe que aún no están registradas?",
        registrar_planificacion, mes_elegido, ids_movimientos
    )
st.caption("Guarda antes de registrar: el registro usa la planificación guardada.")

# ---------- Resumen (se rellena arriba) ----------
variables_restantes = sum(
    num(f.get("Importe")) for f in filas_pagos
    if (texto(f.get("Cuenta")) or CUENTA_PRINCIPAL) == CUENTA_PRINCIPAL
    and pendiente_de_restar(a_texto_fecha(f.get("Fecha")), fecha_corte)
)
ahorro_restante = sum(
    num(f.get("Importe")) for f in filas_ahorro
    if pendiente_de_restar(a_texto_fecha(f.get("Fecha")), fecha_corte)
)
nuevo_saldo = saldo_partida + otros_ingresos - cargos_restantes - variables_restantes
libre = nuevo_saldo - ahorro_restante

with contenedor_resumen:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Saldo de partida", f"{saldo_partida:.2f} €")
    c2.metric("Sonst. Plus", f"{otros_ingresos:.2f} €")
    c3.metric("Cargos fijos restantes", f"{cargos_restantes:.2f} €")
    c4.metric("Pagos variables restantes", f"{variables_restantes:.2f} €")
    c5, c6, c7 = st.columns(3)
    c5.metric("Nuevo saldo previsto", f"{nuevo_saldo:.2f} €")
    c6.metric("Ahorro", f"{ahorro_restante:.2f} €")
    c7.metric("Libre para el mes", f"{libre:.2f} €")
    st.caption(f"{texto_saldo} · Se resta solo lo de Girokonto con fecha posterior al {fecha_corte} (o sin fecha).")

st.subheader("Pagos fijos del mes")

if filas:
    st.dataframe(
        filas,
        hide_index=True,
        width="stretch",
        column_config={
            "Importe": st.column_config.NumberColumn("Importe", format="%.2f €")
        }
    )
    st.caption("✅ Pagado: ya llegó la fecha · ⏳ Registrado: generado, con fecha futura · "
               "📅 Previsto: vista previa, aún no generado · ⚠️ Sin generar: la fecha pasó y falta ejecutar los recurrentes")
else:
    st.info("No hay pagos fijos para este mes.")
    

    # ---------- Exportar a PDF ----------
st.subheader("Exportar")

resumen_pdf = [
    ("Saldo de partida", saldo_partida),
    ("Sonst. Plus", otros_ingresos),
    ("Cargos fijos restantes", cargos_restantes),
    ("Pagos variables restantes", variables_restantes),
    ("Nuevo saldo previsto", nuevo_saldo),
    ("Ahorro", ahorro_restante),
    ("Libre para el mes", libre),
]

fijos_pdf = [[fecha_de(f["Fecha"]), f["Concepto"], f["Cuenta"], f["Cuota"], sin_icono(f["Estado"]), euros(f["Importe"])]
             for f in filas]

variables_pdf = [[fecha_de(f.get("Fecha")), texto(f.get("Concepto")) or "", texto(f.get("Cuenta")) or "",
                  texto(f.get("Categoría")) or "", sin_icono(texto(f.get("Estado")) or "📝 Planificado"),
                  euros(num(f.get("Importe")))]
                 for f in filas_pagos if texto(f.get("Concepto")) or num(f.get("Importe")) > 0]

ahorro_pdf = [[texto(f.get("Cuenta destino")) or "", fecha_de(f.get("Fecha")),
               sin_icono(texto(f.get("Estado")) or "📝 Planificado"), euros(num(f.get("Importe")))]
              for f in filas_ahorro]

pdf_bytes = generar_pdf(mes_elegido, resumen_pdf, f"{texto_saldo} · corte: {fecha_corte}",
                        fijos_pdf, variables_pdf, ahorro_pdf)

st.download_button(
    "📄 Descargar planificación en PDF",
    data=pdf_bytes,
    file_name=f"Planificacion_{mes_elegido}.pdf",
    mime="application/pdf",
)