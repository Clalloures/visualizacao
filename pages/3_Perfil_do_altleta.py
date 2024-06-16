import pandas as pd
import plotly.express as px
import streamlit as st


# função para pegar a quantidade de cada medalha de um atleta em um ano
st.set_page_config(layout="wide")
# Carregar os dados
df = pd.read_csv("athlete_events_pt.csv")


# Renomear as colunas "Sex" e "Sport"
df_unique = df.rename(columns={'Sex': 'Gênero', 'Sport': 'Esporte', 'Medal': 'Medalha', 'Year': 'Ano', 'Age': 'Idade', 'Name': 'Nome'})
df_unique.loc[:, 'Medalha'] = df_unique['Medalha'].replace({'Silver': 'Prata', 'Gold': 'Ouro'})

# Função para filtrar os dados com base na temporada, gênero e esporte
def filter_data(season, gender, sport='Todos'):
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


# ----------------------- # 
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
filtered_df = filter_data(season, gender, sport)


#---------------------------

# Data manipulation
dados_idade_medalha = filtered_df[['Nome', 'Idade', 'Esporte', 'Medalha','Ano','Height']].copy()
dados_idade_medalha['Medalha_number'] = dados_idade_medalha['Medalha'].map({'Bronze': 1, 'Prata': 2, 'Ouro': 3})
dados_idade_medalha['Medalha_number'] = dados_idade_medalha['Medalha_number'].fillna(0)
dados_idade_medalha = dados_idade_medalha.dropna(subset=['Idade'])

# Convert Medalha to categorical with specific order
dados_idade_medalha['Medalha'] = pd.Categorical(dados_idade_medalha['Medalha'], categories=['Bronze', 'Prata', 'Ouro'], ordered=True)

# Stacked and grouped bar plot - Idade group vs Medalhas
bins = pd.interval_range(start=10, end=70, freq=5)
dados_idade_medalha['Idade_group'] = pd.cut(dados_idade_medalha['Idade'], bins)
# Map the intervals to formatted strings in the dataframe
dados_idade_medalha['Idade_group'] = dados_idade_medalha['Idade_group'].apply(lambda x: f'{x.left} a {x.right}')
dados_idade_medalha = dados_idade_medalha.sort_values(by='Idade_group')
title=f'Medalhas por Faixa Etária'
if season != 'Ambas':
    title += f' - Jogos de {season}'
if sport != 'Todos':
    title+=f' - {sport}'
if gender != 'Ambos':
    title+=f' - {gender}'
# Convert to list of strings
formatted_intervals = [f'{interval.left} a {interval.right}' for interval in bins]

fig = px.histogram(dados_idade_medalha, x='Idade_group', color='Medalha', barmode='stack', 
                    title=title, 
                    category_orders={'Idade_group': [str(interval) for interval in bins], 'Medalha': ['Bronze', 'Prata', 'Ouro']}, 
                    color_discrete_map={'Bronze': '#cd7f32', 'Prata': '#c0c0c0', 'Ouro': '#ffd700'})

fig.update_layout(
        title=title,
        barmode='stack',
        xaxis=dict(
            title='Faixa Etária',
            tickmode='array',
            #tickvals=formatted_intervals,
            showgrid=False,  # Hide vertical grid lines
        ),
        yaxis=dict(
            title='Quantidade',
            gridcolor='lightgray',
        ),
        paper_bgcolor='rgba(0,0,0,0)',  # Entire figure background
        plot_bgcolor='rgba(0,0,0,0)',
    )

st.plotly_chart(fig)

#############################
st.subheader('*Comparação da idade média por esporte:*')
st.write('*Filtros ativos:*')
st.write(f'*Temporada*: {season}   |   *Gênero*: {gender}   |   *Esporte*: {sport}')
# Seleção de país pelo usuário
selected_country = st.multiselect(
    "Selecione um ou mais países:",
  sorted(df_unique['País'].unique().tolist()),
  default=None,
  placeholder='Todos'
)
selected_sports = st.multiselect(
    "Selecione um ou mais esportes:",
  sorted(df_unique['Esporte'].unique().tolist()),
  default=None,
  placeholder='Todos'
)

if selected_country != []:
    filtered_df_c = df_unique[df_unique['País'].isin(selected_country)]
else:
    filtered_df_c = df_unique

if selected_sports != []:
    filtered_df_cs = filtered_df_c[filtered_df_c['Esporte'].isin(selected_sports)]
else:
    filtered_df_cs = filtered_df_c
# Grafico de pequenos multiplos geral

# Group by Sport to calculate average age
average_age_sport = filtered_df_cs.dropna(subset=['Idade']).groupby(['Esporte', 'Ano'])['Idade'].mean().reset_index()

# Sort by 'Sport' alphabetically
#average_age_sport = average_age_sport

# Create the plot
fig5 = px.line(
    average_age_sport.sort_values(by=['Esporte', 'Ano']),
    x='Ano',
    y='Idade',
    color='Esporte',
    title='Idade média dos medalhistas por esporte',
    facet_col='Esporte',
    facet_col_wrap=7,
    facet_row_spacing=0.02,
    height=1000,  # Adjust height to fit subplots better
)

# Update layout to adjust appearance
fig5.update_layout(
    xaxis_tickangle=45,
    width=1600,  # Adjust width to make room for all subplots
    margin=dict(l=40, r=40, t=80, b=40),  # Adjust margins to fit the title better
    title={'y': 0.98 , 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
    showlegend=False  # Remove legend for figure
)
fig5.update_yaxes(range=[15, 50])  # Set y-axis limits from 15 to 50 years


# Remove "Sport=" from subplot titles
for annotation in fig5.layout.annotations:
    annotation.text = annotation.text.split('=')[1]

st.plotly_chart(fig5)
