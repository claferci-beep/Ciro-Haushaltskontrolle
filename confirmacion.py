import streamlit as st


@st.dialog("Confirmar cambio")
def _dialogo(mensaje, accion, args):
    st.write(mensaje)
    col1, col2 = st.columns(2)
    if col1.button("✅ Aceptar", type="primary", width="stretch"):
        accion(*args)
        st.session_state["_aviso"] = "Cambio guardado correctamente."
        st.rerun()
    if col2.button("❌ Cancelar", width="stretch"):
        st.rerun()


def confirmar(mensaje, accion, *args):
    """Muestra una ventana Aceptar/Cancelar y solo ejecuta 'accion' si se acepta."""
    _dialogo(mensaje, accion, args)


def mostrar_aviso():
    """Muestra el mensaje de éxito tras un cambio confirmado (llamar al inicio de la página)."""
    if "_aviso" in st.session_state:
        st.success(st.session_state.pop("_aviso"))