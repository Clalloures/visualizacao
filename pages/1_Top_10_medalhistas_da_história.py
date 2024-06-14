import pandas as pd
import plotly.express as px
import streamlit as st

# função para pegar a quantidade de cada medalha de um atleta em um ano
def update_medal_counts(group):
    group = group.sort_values('Year')
    group['Bronze'] = (group['Medal'] == 'Bronze').cumsum()
    group['Silver'] = (group['Medal'] == 'Silver').cumsum()
    group['Gold'] = (group['Medal'] == 'Gold').cumsum()
    group['Total Medal'] = (group['Bronze'] * 1 + group['Silver'] * 2 + group['Gold'] * 3)
    return group

@st.cache_data
def load_data_grouped(df):
    df = df.rename(columns={'Sex': 'Gênero', 'Sport': 'Esporte'})
    df = df.drop(columns=['City','Weight', 'Height'])
    df = df.dropna(subset=['Medal'])
    
    df['Bronze'] = 0
    df['Silver'] = 0
    df['Gold'] = 0
    df['Total Medal'] = 0

    df = df.groupby('ID').apply(update_medal_counts).reset_index(drop=True)
    return df

# Função para filtrar os dados com base na temporada, gênero e esporte
def filter_data(season, gender, sport):
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

def bar_chart_prep(df_filtred):
    filtred_sorted = df_filtred.sort_values('Total Medal')
    filtred_sorted_gruped = filtred_sorted.groupby('Name')[['Bronze', 'Silver', 'Gold','Total Medal']].max().reset_index()
    filtred_sorted_gruped['Quantidade Bronze'] = filtred_sorted_gruped['Bronze'] * 1
    filtred_sorted_gruped['Quantidade Prata'] = filtred_sorted_gruped['Silver'] * 2
    filtred_sorted_gruped['Quantidade Ouro'] = filtred_sorted_gruped['Gold'] * 3

    filtred_sorted_gruped = filtred_sorted_gruped.sort_values(by='Total Medal', ascending=False)
    top10_names = filtred_sorted_gruped['Name'].unique()
    filtred_sorted_gruped_top10 = filtred_sorted_gruped[filtred_sorted_gruped['Name'].isin(top10_names)]
    filtred_sorted_gruped_top10 = filtred_sorted_gruped_top10.head(10)
    filtred_sorted_gruped_top10 = filtred_sorted_gruped_top10.sort_values('Total Medal')
    return filtred_sorted_gruped_top10

def plot_bar_chart_athlete_medals(df):
    tick_values_y = list(range(0, int(df['Total Medal'].max()) + 5, int(df['Total Medal'].max()/5)))
    fig = px.bar(df, x='Name', y=['Quantidade Bronze', 'Quantidade Prata', 'Quantidade Ouro'],
                    title='Maiores medalhista da história',
                    labels={'Name': 'Atleta', 'value': 'Medalhas'},
                    color_discrete_sequence=['#cd7f32', '#c0c0c0', '#ffd700'],
                    barmode='stack',
                    custom_data=['Bronze', 'Silver', 'Gold'])
    fig.update_layout(title_x=0.5,plot_bgcolor='white', paper_bgcolor='white',legend_title_text='Medal',xaxis=dict(showgrid=True, gridcolor='lightgrey'),yaxis=dict(showgrid=True, gridcolor='lightgrey', tickvals=tick_values_y))
    fig.update_traces(hovertemplate='<b>%{x}</b><br>Bronze: %{customdata[0]}<br>Prata: %{customdata[1]}<br>Ouro: %{customdata[2]}')
    fig.update_xaxes(tickangle=90)
    fig.update_layout()
    fig.update_traces(showlegend=True)

    return fig

# Carregar os dados
df = pd.read_csv("athlete_events.csv")
df_unique = load_data_grouped(df)

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
sports.insert(0, 'Todos')  # Adicionando a opção "Todos"
sport = st.selectbox(
    "Selecione o esporte para visualização:",
    sports,
    index=0  # Definindo "Todos" como padrão
)

# Filtrar os dados com base na seleção do usuário
filtred_df = filter_data(season, gender, sport)
bar_chart_df = bar_chart_prep(filtred_df)

fig = plot_bar_chart_athlete_medals(bar_chart_df)
st.plotly_chart(fig)
