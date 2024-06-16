import streamlit as st


st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Dados dos Jogos Olímpicos👋")

st.sidebar.success("Escolha uma das visualizações na barra ao lado.")

st.markdown(
    """
    Projeto desenvolvido para a matéria de Visualização de Dados.

    *Autores:*

    Clarissa Lima Loures

    Giovanna Paranhos Mendes Assis

    Henrique Colonese Echternacht

    Victor Brito Quinino
"""
)
st.write("""
*Bem-vindo à nossa plataforma de visualização das conquistas olímpicas ao longo dos anos! Os Jogos Olímpicos são um momento de celebração global do espírito esportivo, excelência e união. Aqui, você pode explorar estatísticas detalhadas sobre as medalhas conquistadas pelos atletas de diferentes países em várias temporadas.*

**O que esperar:**

1. **Seleção Personalizada:** Escolha entre as temporadas de Verão, Inverno ou visualize ambos os eventos. Além disso, você pode filtrar por gênero para obter uma análise específica.
   
2. **Exploração Detalhada:** Analise o desempenho de um país específico ao longo dos anos, ou compare múltiplos países para uma visão mais ampla.

3. **Gráficos Interativos:** Observe a distribuição de medalhas de ouro, prata e bronze ao longo dos anos com gráficos de barras do tipo Marimekko dinâmicos e informativos.

4. **Tabelas Informativas:** Acompanhe a contagem detalhada de medalhas por ano e explore os detalhes das medalhas conquistadas por um país selecionado.

Dê uma olhada nos números, tendências e histórias por trás das medalhas olímpicas nesta jornada visual através dos Jogos Olímpicos!
""")