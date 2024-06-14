import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide")
# Título e texto introdutório
st.title("Análise da Participação nos Jogos")

# Carregar os dados
df = pd.read_csv("athlete_events_pt.csv")

# Remover duplicatas por país, ano e esporte, mantendo apenas uma medalha por esporte em cada ano
#df_unique = df.drop_duplicates(subset=['NOC', 'Year', 'Sport', 'Sex'])

# Renomear as colunas "Sex" e "Sport"
df_unique = df.rename(columns={'Sex': 'Gênero', 'Sport': 'Esporte', 'Medal': 'Medalha', 'Year': 'Ano'})

# Função para filtrar os dados com base na temporada e gênero
def filter_data(season, gender):
    season_map = {'Verão': 'Summer', 'Inverno': 'Winter', 'Ambas': 'Ambas'}
    gender_map = {'Feminino': 'F', 'Masculino': 'M', 'Ambos': 'Ambos'}
    
    filtered_df = df_unique
    
    if season != 'Ambas':
        filtered_df = filtered_df[filtered_df['Season'] == season_map[season]]
    
    if gender != 'Ambos':
        filtered_df = filtered_df[filtered_df['Gênero'] == gender_map[gender]]

    if sport != 'Todos':
        filtered_df = filtered_df[filtered_df['Esporte'] == sport]
    
    return filtered_df

# Função para agrupar e contar as medalhas
def get_medal_count(filtered_df):
    grouped_df = filtered_df.groupby(['País', 'Ano'])
    medal_count = grouped_df.agg(
        total_medals=('Medalha', 'count'),
        gold_medals=('Medalha', lambda x: (x == 'Gold').sum()),
        silver_medals=('Medalha', lambda x: (x == 'Silver').sum()),
        bronze_medals=('Medalha', lambda x: (x == 'Bronze').sum())
    ).reset_index()
    return medal_count

def create_part_df(df):
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

    result_df = result_df.merge(df[['País', 'NOC']].drop_duplicates(), on='NOC', how='left')
    # Filter out the non-participated rows
    participation_df = result_df[result_df['Participated'] == 1]

    return participation_df

# preenche os anos na base
def fill_in_years(df, unique_years):
    # Ensure all years are represented in the dataframe, even if there are no medals
    all_years = pd.DataFrame({'Ano': unique_years})
    return pd.merge(all_years, df, on='Ano', how='left').fillna(0)

def plot_participation_bar(df):
    # Count the number of participants per year per NOC
    participation_count_df = df.groupby(['Ano', 'País']).size().reset_index(name='Count')

    # Create the stacked bar chart
    fig = px.bar(participation_count_df, x='Ano', y='Count', color='País', title='Participação Olímpica por Ano e País', 
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

def plot_participation_map(df):
    df['Participated'] = df['Participated'].map({1: 'Sim', 0: 'Não'})
    df = df.rename({'Participated': 'Participação'}, axis=1)
    df = df.sort_values(by='Ano')
    fig = px.choropleth(df, 
                        locations="NOC",
                        color="Participação",
                        hover_name="País",
                        title='Países Participantes das Olimpíadas',
                        animation_frame='Ano',
                        color_discrete_map={'Sim': 'red', 'Não': 'grey'}
                        )  # Escolha uma escala de cores adequada
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

# Seleção de esporte pelo usuário
sports = df_unique['Esporte'].unique().tolist()
sports.sort()
sports.insert(0, 'Todos')  # Adicionando a opção "Todos"
sport = st.selectbox(
    "Selecione o esporte para visualização:",
    sports,
    index=0  # Definindo "Todos" como padrão
)

# Filtrar os dados com base na seleção do usuário
filtered_df = filter_data(season, gender)
part_df = create_part_df(filtered_df)

# Plotar mapa de participação
fig2 = plot_participation_map(part_df)
st.plotly_chart(fig2)

# Plotar tabela de participação
sum_df = part_df.groupby(['País']).count().reset_index().drop('Ano', axis=1)
sum_df = sum_df.rename({'Participated': 'Participações'}, axis=1)
sum_df = sum_df.sort_values(by='Participações', ascending=False).reset_index().drop('index', axis=1)
sum_df.index += 1
st.subheader('Participações por país ao longo do tempo')
# Seleção de país pelo usuário
selected_country = st.multiselect(
    "Selecione um ou mais países:",
  sorted(df_unique['País'].unique().tolist()),
  default=None,
  placeholder='Todos'
)

if selected_country != []:
    filtered_df_c = part_df[part_df['País'].isin(selected_country)]
else:
    filtered_df_c = part_df
# Criando o gráfico de barras
fig = plot_participation_bar(filtered_df_c)
# Exibir o gráfico de barras
st.plotly_chart(fig)

st.subheader('*Países com maior número de participações nos Jogos Olímpicos:*')
st.write('*Filtros ativos:*')
st.write(f'Temporada: {season}   |   Gênero: {gender}   |   Esporte: {sport}')
st.write(sum_df.drop('NOC', axis=1))