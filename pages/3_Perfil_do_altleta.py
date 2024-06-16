import pandas as pd
import plotly.express as px
import streamlit as st


# função para pegar a quantidade de cada medalha de um atleta em um ano
st.set_page_config(layout="wide")
# Carregar os dados
df = pd.read_csv("athlete_events_pt.csv")

st.title('Perfil dos atletas')
# Renomear as colunas "Sex" e "Sport"
df_unique = df.rename(columns={'Sex': 'Gênero', 'Sport': 'Esporte', 'Medal': 'Medalha', 'Year': 'Ano', 'Age': 'Idade', 'Name': 'Nome', 'Height': 'Altura'})
df_unique.loc[:, 'Medalha'] = df_unique['Medalha'].replace({'Silver': 'Prata', 'Gold': 'Ouro'})
df_unique.loc[:, 'Altura'] = df_unique['Altura']/100
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


def plot_in_mult(df, yaxis):
        # Create the plot
        fig5 = px.line(
            df.sort_values(by=['Esporte', 'Ano']),
            x='Ano',
            y=str(yaxis),
            color='Esporte',
            title=f'{str(yaxis)} média dos medalhistas por esporte',
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
       
        # Remove "Sport=" from subplot titles
        for annotation in fig5.layout.annotations:
            annotation.text = annotation.text.split('=')[1]
        return fig5

def boxplot_sports(df, yaxis):
    fig2 = px.box(df.dropna(subset=yaxis), x='Esporte', y=str(yaxis), title=f'Boxplot da {yaxis} por Esporte', hover_data=['Nome'])
    fig2.update_layout(xaxis={'categoryorder': 'category ascending'}, xaxis_tickangle=90,
    height=1000,
    title_x=0.4)
    return fig2

def histogram_medals(df):

    dados_idade_medalha = df.dropna(subset=['Idade'])

    # Convert Medalha to categorical with specific order
    dados_idade_medalha['Medalha'] = pd.Categorical(dados_idade_medalha['Medalha'], categories=['Bronze', 'Prata', 'Ouro'], ordered=True)

    # Stacked and grouped bar plot - Idade group vs Medalhas
    bins = pd.interval_range(start=10, end=70, freq=5)
    dados_idade_medalha['Idade_group'] = pd.cut(dados_idade_medalha['Idade'], bins)
    # Map the intervals to formatted strings in the dataframe
    dados_idade_medalha['Idade_group'] = dados_idade_medalha['Idade_group'].apply(lambda x: f'{x.left} a {x.right}')
    dados_idade_medalha = dados_idade_medalha.sort_values(by='Idade_group')
    title='Medalhas por Faixa Etária'
    if season != 'Ambas':
        title += f' - Jogos de {season}'
    if sport != 'Todos':
        title+=f' - {sport}'
    if gender != 'Ambos':
        title+=f' - {gender}'
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
                showgrid=False,  # Hide vertical grid lines
            ),
            yaxis=dict(
                title='Quantidade',
                gridcolor='lightgray',
            ),
            paper_bgcolor='rgba(0,0,0,0)',  # Entire figure background
            plot_bgcolor='rgba(0,0,0,0)',
            title_x=0.4,
            height=600
        )
    return fig
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
# Data manipulation
dados_idade_medalha = filtered_df[['Nome', 'Idade', 'Esporte', 'Medalha','Ano','Altura']].copy()
dados_idade_medalha['Medalha_number'] = dados_idade_medalha['Medalha'].map({'Bronze': 1, 'Prata': 2, 'Ouro': 3})
dados_idade_medalha['Medalha_number'] = dados_idade_medalha['Medalha_number'].fillna(0)

#---------------------------

st.subheader('Medalhas por faixa etária')
# Sort by 'Sport' alphabetically
if len(filtered_df) == 0:
    st.write('Nenhum dado para os filtros selecionados.')
else:
    fig = histogram_medals(dados_idade_medalha)
    st.plotly_chart(fig)

#############################
st.subheader('Perfil médio por esporte')
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
selected_year = st.multiselect(
    "Selecione um ou mais anos:",
  sorted(df_unique['Ano'].unique().tolist()),
  default=None,
  placeholder='Todos'
)
if selected_year != []:
    filtered_df_cs = filtered_df_cs[filtered_df_cs['País'].isin(selected_country)]
else:
    filtered_df_cs = filtered_df_cs

# Function to update the boxplot based on selected year and Y axis
yaxis = st.selectbox(
    "Selecione eixo y:",
    ['Altura', 'Idade'],
    index=0  
)

# Sort by 'Sport' alphabetically
if len(filtered_df_cs) == 0:
    st.write('Nenhum dado para os filtros selecionados.')
else:
    # Group by Sport to calculate average age
    average_age_sport = filtered_df_cs.dropna(subset=[str(yaxis)]).groupby(['Esporte', 'Ano'])[str(yaxis)].mean().reset_index()
    fig5 = plot_in_mult(average_age_sport, yaxis)
    st.plotly_chart(fig5)

    fig2 = boxplot_sports(filtered_df_cs, yaxis)
    st.plotly_chart(fig2)
    