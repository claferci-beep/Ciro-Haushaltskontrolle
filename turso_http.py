import requests
import streamlit as st

TURSO_URL = st.secrets["turso_url"].replace("libsql://", "https://") + "/v2/pipeline"
TURSO_TOKEN = st.secrets["turso_token"]


def convertir_valor(valor):
    if valor is None:
        return {"type": "null"}
    if isinstance(valor, bool):
        return {"type": "integer", "value": str(int(valor))}
    if isinstance(valor, int):
        return {"type": "integer", "value": str(valor)}
    if isinstance(valor, float):
        return {"type": "float", "value": valor}
    return {"type": "text", "value": str(valor)}


def ejecutar(sql, parametros=None):
    stmt = {"sql": sql}
    if parametros:
        stmt["args"] = [convertir_valor(p) for p in parametros]

    cuerpo = {
        "requests": [
            {"type": "execute", "stmt": stmt},
            {"type": "close"}
        ]
    }

    headers = {
        "Authorization": f"Bearer {TURSO_TOKEN}",
        "Content-Type": "application/json"
    }

    respuesta = requests.post(TURSO_URL, headers=headers, json=cuerpo)
    respuesta.raise_for_status()
    datos = respuesta.json()

    primer_resultado = datos["results"][0]
    if primer_resultado.get("type") == "error":
        raise Exception(f"Error de Turso: {primer_resultado['error']}")

    resultado = primer_resultado["response"]["result"]
    columnas = [c["name"] for c in resultado["cols"]]

    filas = []
    for fila in resultado["rows"]:
        registro = {}
        for i, celda in enumerate(fila):
            valor = celda.get("value")
            if celda.get("type") == "integer" and valor is not None:
                valor = int(valor)
            registro[columnas[i]] = valor
        filas.append(registro)

    return filas, resultado.get("last_insert_rowid")