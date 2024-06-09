import pandas as pd
import plotly.express as px
import streamlit as st

# Carregar os dados
df = pd.read_csv("/home/dell/Documentos/Mestrado/ProjetoVisualizacao/data/athlete_events.csv")

# Remover duplicatas por país, ano e esporte, mantendo apenas uma medalha por esporte em cada ano
#df_unique = df.drop_duplicates(subset=['NOC', 'Year', 'Sport', 'Sex'])

df_unique = df
# Renomear as colunas "Sex" e "Sport"
df_unique = df_unique.rename(columns={'Sex': 'Gênero', 'Sport': 'Esporte'})

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

# Função para agrupar e contar as medalhas
def get_medal_count(filtered_df):
    grouped_df = filtered_df.groupby(['NOC', 'Year'])
    medal_count = grouped_df.agg(
        total_medals=('Medal', 'count')
    ).reset_index()
    return medal_count

# Função para calcular a quantidade de medalhas por esporte e ano para cada país
def get_detailed_medal_info(filtered_df):
    detailed_medal_count = filtered_df.groupby(['NOC', 'Year', 'Esporte', 'Gênero']).size().reset_index(name='count')
    return detailed_medal_count

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
filtered_df = filter_data(season, gender, sport)
medal_count = get_medal_count(filtered_df)
detailed_medal_info = get_detailed_medal_info(filtered_df)

all_countries = pd.DataFrame({"NOC": 
                              ["AFG", "ALB", "ALG", "AND", "ANG", "ANT", "ARG", "ARM", "ARU", "ASA", 
                               "AUS", "AUT", "AZE", "BAH", "BAN", "BAR", "BDI", "BEL", "BEN", "BER", 
                               "BHU", "BIH", "BIZ", "BLR", "BOL", "BOT", "BRA", "BRN", "BRU", "BUL", 
                               "BUR", "CAF", "CAM", "CAN", "CAY", "CGO", "CHA", "CHI", "CHN", "CIV", 
                               "CMR", "COD", "COK", "COL", "COM", "CPV", "CRC", "CRO", "CUB", "CYP", 
                               "CZE", "DEN", "DJI", "DMA", "DOM", "ECU", "EGY", "ERI", "ESA", "ESP", 
                               "EST", "ETH", "FIJ", "FIN", "FRA", "FSM", "GAB", "GAM", "GBR", "GBS", 
                               "GEO", "GEQ", "GER", "GHA", "GRE", "GRN", "GUA", "GUI", "GUM", "GUY", 
                               "HAI", "HKG", "HON", "HUN", "INA", "IND", "IOA", "IRI", "IRL", "IRQ", 
                               "ISL", "ISR", "ISV", "ITA", "IVB", "JAM", "JOR", "JPN", "KAZ", "KEN", 
                               "KGZ", "KIR", "KOR", "KOS", "KSA", "KUW", "LAO", "LAT", "LBA", "LBN", 
                               "LBR", "LCA", "LES", "LIE", "LTU", "LUX", "MAD", "MAR", "MAS", "MAW", 
                               "MDA", "MDV", "MEX", "MGL", "MHL", "MKD", "MLI", "MLT", "MNE", "MON", 
                               "MOZ", "MRI", "MTN", "MYA", "NAM", "NCA", "NED", "NEP", "NGR", "NIG", 
                               "NOR", "NRU", "NZL", "OMA", "PAK", "PAN", "PAR", "PER", "PHI", "PLE", 
                               "PLW", "PNG", "POL", "POR", "PRK", "PUR", "QAT", "ROU", "RSA", "RUS", 
                               "RWA", "SAM", "SEN", "SEY", "SGP", "SKN", "SLE", "SLO", "SMR", "SOL", 
                               "SOM", "SRB", "SRI", "SSD", "STP", "SUD", "SUI", "SUR", "SVK", "SWE", 
                               "SWZ", "SYR", "TAN", "TGA", "THA", "TJK", "TKM", "TLS", "TOG", "TPE", 
                               "TTO", "TUN", "TUR", "TUV", "UAE", "UGA", "UKR", "URU", "USA", "UZB", 
                               "VAN", "VAT", "VEN", "VIE", "VIN", "YEM", "ZAM", "ZIM"]})

# Mesclar medal_count com all_countries para garantir que todos os países estejam presentes
medal_count_all = pd.merge(all_countries, medal_count, on="NOC", how="left").fillna(0)

# Criar o gráfico cloropleth
fig = px.choropleth(medal_count_all, 
                    locations="NOC",
                    color="total_medals",
                    hover_name="NOC",
                    hover_data=['total_medals'],
                    title=f'Total de Medalhas por País ({season})',
                    animation_frame='Year',
                    color_continuous_scale=px.colors.sequential.Blues)  # Escolha uma escala de cores adequada

# Atualizar o layout para definir a cor dos países sem medalhas
fig.update_traces(marker=dict(line=dict(color='rgb(255,255,255)', width=1)))  # Borda branca
fig.update_traces(marker_line_color='gray', marker_line_width=0.5)  # Borda cinza
fig.update_traces(marker_opacity=0.8)  # Opacidade dos países com medalhas


# Exibir o gráfico de cloropleth
st.plotly_chart(fig)

# Ordenar a tabela de quantidade total de medalhas por país pelo ano
medal_count_sorted = medal_count.sort_values(by='Year')

# Botões para ordenação da tabela de quantidade total de medalhas por país
st.subheader(f"Quantidade Total de Medalhas por País ({season})")
order_by_medals_button = st.checkbox('Ordenar por número de medalhas (Países)', key='order_by_medals_button')
order_by_year_button = st.checkbox('Ordenar por ano (Países)', key='order_by_year_button')

# Ordenar a tabela conforme os botões selecionados
if order_by_medals_button:
    medal_count_sorted = medal_count_sorted.sort_values(by='total_medals', ascending=False)

if order_by_year_button:
    medal_count_sorted = medal_count_sorted.sort_values(by='Year')

# Adicionando a coluna "Temporada" à tabela de quantidade total de medalhas por país
medal_count_sorted_with_season = medal_count_sorted.copy()
medal_count_sorted_with_season['Temporada'] = season

# Tabela de quantidade total de medalhas por país
st.write(medal_count_sorted_with_season.rename(columns={'total_medals': 'Quantidade Medalhas', 'Year': 'Ano'}).astype({'Ano': int}))

# Botões para ordenação da tabela de detalhes das medalhas
st.subheader("Detalhes de Medalhas por País, Ano, Esporte e Gênero")
order_by_medals_button_detailed = st.checkbox('Ordenar por número de medalhas (Detalhes)', key='order_by_medals_button_detailed')
order_by_year_button_detailed = st.checkbox('Ordenar por ano (Detalhes)', key='order_by_year_button_detailed')

# Ordenar a tabela conforme os botões selecionados
detailed_medal_info_sorted = detailed_medal_info
if order_by_medals_button_detailed:
    detailed_medal_info_sorted = detailed_medal_info_sorted.sort_values(by='count', ascending=False)

if order_by_year_button_detailed:
    detailed_medal_info_sorted = detailed_medal_info_sorted.sort_values(by='Year')

# Adicionando a coluna "Temporada" à tabela de detalhes das medalhas
detailed_medal_info_sorted_with_season = detailed_medal_info_sorted.copy()
detailed_medal_info_sorted_with_season['Temporada'] = season

# Tabela de detalhes das medalhas por país, ano, esporte e gênero
st.write(detailed_medal_info_sorted_with_season.rename(columns={'count': 'Quantidade Medalhas', 'Year': 'Ano'}).astype({'Ano': int}))
