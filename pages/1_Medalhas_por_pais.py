import pandas as pd
import plotly.express as px
import streamlit as st

# Título e texto introdutório
st.title("Análise Visual das Medalhas Olímpicas")
st.write("""
Bem-vindo à nossa plataforma de visualização das conquistas olímpicas ao longo dos anos! Os Jogos Olímpicos são um momento de celebração global do espírito esportivo, excelência e união. Aqui, você pode explorar estatísticas detalhadas sobre as medalhas conquistadas pelos atletas de diferentes países em várias temporadas.

**O que esperar:**

1. **Seleção Personalizada:** Escolha entre as temporadas de Verão, Inverno ou visualize ambos os eventos. Além disso, você pode filtrar por gênero para obter uma análise específica.
   
2. **Exploração Detalhada:** Analise o desempenho de um país específico ao longo dos anos, ou compare múltiplos países para uma visão mais ampla.

3. **Gráficos Interativos:** Observe a distribuição de medalhas de ouro, prata e bronze ao longo dos anos com gráficos de barras dinâmicos e informativos.

4. **Tabelas Informativas:** Acompanhe a contagem detalhada de medalhas por ano e explore os detalhes das medalhas conquistadas por um país selecionado.

Dê uma olhada nos números, tendências e histórias por trás das medalhas olímpicas nesta jornada visual através dos Jogos Olímpicos!
""")

# Carregar os dados
df = pd.read_csv("/home/dell/Documentos/Mestrado/ProjetoVisualizacao/data/athlete_events.csv")

# Remover duplicatas por país, ano e esporte, mantendo apenas uma medalha por esporte em cada ano
#df_unique = df.drop_duplicates(subset=['NOC', 'Year', 'Sport', 'Sex'])

df_unique = df
# Renomear as colunas "Sex" e "Sport"
df_unique = df_unique.rename(columns={'Sex': 'Gênero', 'Sport': 'Esporte', 'Medal': 'Medalha'})

# Função para filtrar os dados com base na temporada e gênero
def filter_data(season, gender):
    season_map = {'Verão': 'Summer', 'Inverno': 'Winter', 'Ambas': 'Ambas'}
    gender_map = {'Feminino': 'F', 'Masculino': 'M', 'Ambos': 'Ambos'}
    
    filtered_df = df_unique
    
    if season != 'Ambas':
        filtered_df = filtered_df[filtered_df['Season'] == season_map[season]]
    
    if gender != 'Ambos':
        filtered_df = filtered_df[filtered_df['Gênero'] == gender_map[gender]]
    
    return filtered_df

# Função para agrupar e contar as medalhas
def get_medal_count(filtered_df):
    grouped_df = filtered_df.groupby(['NOC', 'Year'])
    medal_count = grouped_df.agg(
        total_medals=('Medalha', 'count'),
        gold_medals=('Medalha', lambda x: (x == 'Gold').sum()),
        silver_medals=('Medalha', lambda x: (x == 'Silver').sum()),
        bronze_medals=('Medalha', lambda x: (x == 'Bronze').sum())
    ).reset_index()
    return medal_count

# Seleção de temporada pelo usuário
season = st.selectbox(
    "Selecione a temporada para visualização:",
    ("Ambas", "Verão", "Inverno"),
    index=0  # Definindo "Ambas" como padrão
)

# Seleção de gênero pelo usuário
gender = st.selectbox(
    "Selecione o gênero para visualização:",
    ("Ambos", "Feminino", "Masculino"),
    index=0  # Definindo "Ambos" como padrão
)

# Seleção de país pelo usuário
selected_country = st.selectbox(
    "Selecione um país ou todos:",
    ["Todos"] + sorted(df_unique['NOC'].unique().tolist()),
    index=0
)

# Filtrar os dados com base na seleção do usuário
if selected_country == "Todos":
    filtered_df = filter_data(season, gender)
else:
    filtered_df = filter_data(season, gender)
    filtered_df = filtered_df[filtered_df['NOC'] == selected_country]

# Obtendo contagem de medalhas
medal_count = get_medal_count(filtered_df)

# Criando o gráfico de barras
fig = px.bar(medal_count, 
             x='Year', 
             y=['gold_medals', 'silver_medals', 'bronze_medals'], 
             title=f'Quantidade de Medalhas por Tipo ({season})',
             labels={'value': 'Quantidade de Medalhas', 'variable': 'Tipo de Medalha'},
             color_discrete_sequence=['gold', 'silver', 'saddlebrown']
            )

# Adicionar o nome do país ao passar o mouse sobre o gráfico
fig.update_traces(hovertemplate='Ano: %{x}<br>Tipo de Medalha: %{variable}<br>Quantidade: %{y}<br>País: %{meta[0]}')
fig.update_traces(meta=medal_count['NOC'])

fig.update_layout(barmode='stack')

# Exibir o gráfico de barras
st.plotly_chart(fig)

# Tabela de contagem de medalhas
st.subheader("Contagem de Medalhas por Ano")

# Botões para ordenar a tabela
sort_by = st.selectbox("Ordenar por:", ["Ano", "Total", "Ouro", "Prata", "Bronze", "País"])

# Ordenar a tabela de acordo com a seleção do usuário
if sort_by == "Ano":
    medal_count_sorted = medal_count.sort_values(by=['Year'])
if sort_by == "País":
    medal_count_sorted = medal_count.sort_values(by=['NOC'])
elif sort_by == "Total":
    medal_count_sorted = medal_count.sort_values(by=['total_medals'], ascending=False)
elif sort_by == "Ouro":
    medal_count_sorted = medal_count.sort_values(by=['gold_medals'], ascending=False)
elif sort_by == "Prata":
    medal_count_sorted = medal_count.sort_values(by=['silver_medals'], ascending=False)
elif sort_by == "Bronze":
    medal_count_sorted = medal_count.sort_values(by=['bronze_medals'], ascending=False)

# Exibir a tabela ordenada
st.write(medal_count_sorted.rename(columns={'total_medals': 'Total', 'gold_medals': 'Ouro', 'silver_medals': 'Prata', 'bronze_medals': 'Bronze'}).astype({'Year': str}))

# Exibir detalhes apenas se um país específico for selecionado
if selected_country != "Todos":
    st.subheader(f"Detalhes das Medalhas para {selected_country}")
    st.write(filtered_df[['Year', 'Medalha']].groupby('Year').count().rename(columns={'Medalha': 'Total de Medalhas'}).astype({'Total de Medalhas': int})).astype({'Ano': str})

