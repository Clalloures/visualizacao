import streamlit as st


st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Dados Olimpiadas👋")

st.sidebar.success("Escolha uma das visualizações na barra ao lado.")

st.markdown(
    """
    Projeto desenvolvido para automação da persona Kunumi.
"""
)