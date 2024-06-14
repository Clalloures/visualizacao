import streamlit as st


st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Dados dos Jogos Plímpicos👋")

st.sidebar.success("Escolha uma das visualizações na barra ao lado.")

st.markdown(
    """
    Projeto desenvolvido para a matéria de Visualização de Dados.

    Autores:

    Clarissa Lima Loures
    Giovanna Paranhos Mendes Assis
    Henrique Colonese Echternacht
    Victor Brito Quinino
"""
)