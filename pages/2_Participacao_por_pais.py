import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go

# Título e texto introdutório
st.title("Análise Visual das Medalhas Olímpicas")
st.write("""
Bem-vindo à nossa plataforma de visualização das conquistas olímpicas ao longo dos anos! Os Jogos Olímpicos são um momento de celebração global do espírito esportivo, excelência e união. Aqui, você pode explorar estatísticas detalhadas sobre as medalhas conquistadas pelos atletas de diferentes países em várias temporadas.

**O que esperar:**

1. **Seleção Personalizada:** Escolha entre as temporadas de Verão, Inverno ou visualize ambos os eventos. Além disso, você pode filtrar por gênero para obter uma análise específica.
   
2. **Exploração Detalhada:** Analise o desempenho de um país específico ao longo dos anos, ou compare múltiplos países para uma visão mais ampla.

3. **Gráficos Interativos:** Observe a distribuição de medalhas de ouro, prata e bronze ao longo dos anos com gráficos de barras do tipo Marimekko dinâmicos e informativos.

4. **Tabelas Informativas:** Acompanhe a contagem detalhada de medalhas por ano e explore os detalhes das medalhas conquistadas por um país selecionado.

Dê uma olhada nos números, tendências e histórias por trás das medalhas olímpicas nesta jornada visual através dos Jogos Olímpicos!
""")

# Carregar os dados
df = pd.read_csv("../athlete_events.csv")

# Remover duplicatas por país, ano e esporte, mantendo apenas uma medalha por esporte em cada ano
#df_unique = df.drop_duplicates(subset=['NOC', 'Year', 'Sport', 'Sex'])

df_unique = df
# Renomear as colunas "Sex" e "Sport"
df_unique = df_unique.rename(columns={'Sex': 'Gênero', 'Sport': 'Esporte', 'Medal': 'Medalha', 'Year': 'Ano'})

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
    grouped_df = filtered_df.groupby(['NOC', 'Ano'])
    medal_count = grouped_df.agg(
        total_medals=('Medalha', 'count'),
        gold_medals=('Medalha', lambda x: (x == 'Gold').sum()),
        silver_medals=('Medalha', lambda x: (x == 'Silver').sum()),
        bronze_medals=('Medalha', lambda x: (x == 'Bronze').sum())
    ).reset_index()
    return medal_count

# preenche os anos na base
def fill_in_years(df, unique_years):
    # Ensure all years are represented in the dataframe, even if there are no medals
    all_years = pd.DataFrame({'Ano': unique_years})
    return pd.merge(all_years, df, on='Ano', how='left').fillna(0)

def plot_participation_bar(df):
    olympic_years = df['Ano'].unique()
    olympic_years_df = pd.DataFrame(olympic_years, columns=['Ano'])

    df_grouped = df[['Ano', 'NOC']].groupby(['Ano', 'NOC']).count().reset_index()

    # Function to check participation
    def check_participation(year, noc, df):
        return 1 if ((df['Ano'] == year) & (df['NOC'] == noc)).any() else 0

    # Create a list of all NOCs
    nocs = df['NOC'].unique()

    # Create a new DataFrame to store the results
    result_df = pd.DataFrame()

    # Populate the result DataFrame
    for noc in nocs:
        noc_df = olympic_years_df.copy()
        noc_df['NOC'] = noc
        noc_df['Participated'] = noc_df.apply(lambda row: check_participation(row['Ano'], row['NOC'], df_grouped), axis=1)
        result_df = pd.concat([result_df, noc_df], ignore_index=True)
    # Filter out the non-participated rows
    participation_df = result_df[result_df['Participated'] == 1]

    # Count the number of participants per year per NOC
    participation_count_df = participation_df.groupby(['Ano', 'NOC']).size().reset_index(name='Count')

    # Create the stacked bar chart
    fig = px.bar(participation_count_df, x='Ano', y='Count', color='NOC', title='Participação Olímpica por Ano e País', 
                labels={'Count': 'Número de Países Participantes'}, 
                barmode='stack')
        # Update layout for the Marimekko chart
    fig.update_layout(
            barmode='stack',
            xaxis=dict(
                title='Ano',
                tickmode='array',
                tickvals=df['Ano'],
                showgrid=False,  # Hide vertical grid lines
                ),
            yaxis=dict(
                gridcolor='lightgray',
            ),
            paper_bgcolor='rgba(0,0,0,0)',  # Entire figure background
            plot_bgcolor='rgba(0,0,0,0)'
            #width=1500,  # Set figure width
            #height=600,  # Set figure height
        )
    # Show the figure
    return fig

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
selected_country = st.multiselect(
    "Selecione um ou mais países:",
  sorted(df_unique['NOC'].unique().tolist()),
  default=None,
  placeholder='Todos'
)
# Filtrar os dados com base na seleção do usuário
if selected_country == []:
    filtered_df = filter_data(season, gender)
else:
    filtered_df = filter_data(season, gender)
    filtered_df = filtered_df[filtered_df['NOC'].isin(selected_country)]

# Criando o gráfico de barras
fig = plot_participation_bar(filtered_df)

# Exibir o gráfico de barras
st.plotly_chart(fig)

