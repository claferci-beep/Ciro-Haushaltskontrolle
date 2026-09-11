import streamlit as st

def verificar_password():
    def password_correcto():
        if st.session_state["password_input"] == st.secrets["password"]:
            st.session_state["autenticado"] = True
            del st.session_state["password_input"]
        else:
            st.session_state["autenticado"] = False

    if "autenticado" not in st.session_state:
        st.text_input("Contraseña", type="password", on_change=password_correcto, key="password_input")
        st.stop()
    elif not st.session_state["autenticado"]:
        st.text_input("Contraseña", type="password", on_change=password_correcto, key="password_input")
        st.error("Contraseña incorrecta")
        st.stop()