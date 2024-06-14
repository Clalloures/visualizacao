import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide")
# Carregar os dados
df = pd.read_csv("../athlete_events.csv")
# Dicionário de traduções
traducoes = {
    'Basketball': 'Basquete',
    'Judo': 'Judô',
    'Football': 'Futebol',
    'Tug-Of-War': 'Cabo de Guerra',
    'Speed Skating': 'Patinação de Velocidade',
    'Cross Country Skiing': 'Esqui Cross-Country',
    'Athletics': 'Atletismo',
    'Ice Hockey': 'Hóquei no Gelo',
    'Swimming': 'Natação',
    'Badminton': 'Badminton',
    'Sailing': 'Vela',
    'Biathlon': 'Biatlo',
    'Gymnastics': 'Ginástica',
    'Art Competitions': 'Competições de Arte',
    'Alpine Skiing': 'Esqui Alpino',
    'Handball': 'Handebol',
    'Weightlifting': 'Levantamento de Peso',
    'Wrestling': 'Luta',
    'Luge': 'Luge',
    'Water Polo': 'Pólo Aquático',
    'Hockey': 'Hóquei',
    'Rowing': 'Remo',
    'Bobsleigh': 'Bobsled',
    'Fencing': 'Esgrima',
    'Equestrianism': 'Hipismo',
    'Shooting': 'Tiro',
    'Boxing': 'Boxe',
    'Taekwondo': 'Taekwondo',
    'Cycling': 'Ciclismo',
    'Diving': 'Saltos Ornamentais',
    'Canoeing': 'Canoagem',
    'Tennis': 'Tênis',
    'Modern Pentathlon': 'Pentatlo Moderno',
    'Figure Skating': 'Patinação Artística',
    'Golf': 'Golfe',
    'Softball': 'Softbol',
    'Archery': 'Tiro com Arco',
    'Volleyball': 'Voleibol',
    'Synchronized Swimming': 'Nado Sincronizado',
    'Table Tennis': 'Tênis de Mesa',
    'Nordic Combined': 'Combinado Nórdico',
    'Baseball': 'Beisebol',
    'Rhythmic Gymnastics': 'Ginástica Rítmica',
    'Freestyle Skiing': 'Esqui Estilo Livre',
    'Rugby Sevens': 'Rugby de Sete',
    'Trampolining': 'Ginástica de Trampolim',
    'Beach Volleyball': 'Vôlei de Praia',
    'Triathlon': 'Triatlo',
    'Ski Jumping': 'Salto de Esqui',
    'Curling': 'Curling',
    'Snowboarding': 'Snowboard',
    'Rugby': 'Rugby',
    'Short Track Speed Skating': 'Patinação de Velocidade em Pista Curta',
    'Skeleton': 'Skeleton',
    'Lacrosse': 'Lacrosse',
    'Polo': 'Pólo',
    'Cricket': 'Críquete',
    'Racquets': 'Raquetes',
    'Motorboating': 'Motonáutica',
    'Military Ski Patrol': 'Patrulha Militar de Esqui',
    'Croquet': 'Croquet',
    'Jeu De Paume': 'Jeu De Paume',
    'Roque': 'Roque',
    'Alpinism': 'Alpinismo',
    'Basque Pelota': 'Pelota Basca',
    'Aeronautics': 'Aeronáutica'
}
# Mapping the dictionary to the DataFrame column
df['Sport'] = df['Sport'].map(traducoes)

# Remover duplicatas por país, ano e esporte, mantendo apenas uma medalha por esporte em cada ano

df_unique = df
# Renomear as colunas "Sex" e "Sport"
df_unique = df_unique.rename(columns={'Sex': 'Gênero', 'Sport': 'Esporte', 'Medal': 'Medalha', 'Year': 'Ano'})

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

# Função para agrupar e contar as medalhas
def get_medal_count(filtered_df):
    grouped_df = filtered_df.groupby(['NOC', 'Ano'])
    medal_count = grouped_df.agg(
        total_medals=('Medalha', 'count')
    ).reset_index()
    return medal_count

# Função para calcular a quantidade de medalhas por esporte e ano para cada país
def get_detailed_medal_info(filtered_df):
    detailed_medal_count = filtered_df.groupby(['NOC', 'Ano', 'Esporte', 'Gênero']).size().reset_index(name='count')
    return detailed_medal_count

# preenche os anos na base
def fill_in_years(df, unique_years):
    # Ensure all years are represented in the dataframe, even if there are no medals
    all_years = pd.DataFrame({'Ano': unique_years})
    return pd.merge(all_years, df, on='Ano', how='left').fillna(0)

# cria o mekko chart
def plot_marimekko(dataframe, country):
    unique_years = sorted(dataframe['Ano'].unique())  # Ensure unique_years are sorted
    # Filter data for the specified country
    df_country = dataframe[dataframe['NOC'] == country]
    df_country.loc[:, 'Medalha'] = df_country['Medalha'].replace({'Silver': 'Prata', 'Gold': 'Ouro'})

    # Group by year and medal type and count the number of medals
    medal_counts = df_country.groupby(['Ano', 'Medalha']).size().reset_index(name='count')
    medal_counts = fill_in_years(medal_counts, unique_years)
    
    # Pivot the dataframe to have medal types as columns
    medal_pivot = medal_counts.pivot(index='Ano', columns='Medalha', values='count').fillna(0)

    # Calculate total medals per year and proportions for each medal type
    medal_pivot['total'] = medal_pivot.sum(axis=1)
    for medal in ['Ouro', 'Prata', 'Bronze']:
        if medal not in medal_pivot.columns:
            medal_pivot[f'Medalhas de {medal}'] = 0
            medal_pivot[medal] = 0
        else:
            medal_pivot[f'Medalhas de {medal}'] = medal_pivot[medal] / medal_pivot['total']

    # Normalize widths based on the total medals to fit the graph size
    total_medals = medal_pivot['total'].sum()
    medal_pivot['width'] = medal_pivot['total'] / total_medals
    medal_pivot['width'] = medal_pivot['width'].fillna(0)

    # Compute the x positions for bars to ensure they are properly centered
    bar_width = 1 / len(unique_years)  # Adjust bar width to fit the number of years
    if len(unique_years) < 20 or total_medals < 10:
        padding = len(unique_years)/30  # Padding between bars
    else: 
        padding = 0.1
    x_positions = [i * (bar_width + padding) for i in range(len(unique_years))]
    medal_pivot['x'] = x_positions

    # Create the Marimekko chart with adjusted x-axis
    fig = go.Figure()

    # Add bronze trace first
    fig.add_trace(go.Bar(
        x=medal_pivot['x'],
        y=medal_pivot['Medalhas de Bronze'],
        width=medal_pivot['width'],
        marker=dict(color='#cd7f32'),
        name='Bronze',
        customdata=medal_pivot['Bronze'],
        hovertemplate='Year: %{x}<br>Medalhas de Bronze: %{customdata}<br>Proporção de Bronzes: %{y:.2f}<extra></extra>',
    ))

    # Add silver trace second
    fig.add_trace(go.Bar(
        x=medal_pivot['x'],
        y=medal_pivot['Medalhas de Prata'],
        width=medal_pivot['width'],
        marker=dict(color='#c0c0c0'),
        name='Prata',
        customdata=medal_pivot['Prata'],
        hovertemplate='Year: %{x}<br>Medalhas de Prata: %{customdata}<br>Proporção de Pratas: %{y:.2f}<extra></extra>',
    ))

    # Add gold trace last
    fig.add_trace(go.Bar(
        x=medal_pivot['x'],
        y=medal_pivot['Medalhas de Ouro'],
        width=medal_pivot['width'],
        marker=dict(color='#ffd700'),
        name='Ouro',
        customdata=medal_pivot['Ouro'],
        text=medal_pivot.apply(lambda row: row['total'] if row['total'] > 0 else '', axis=1),
        textposition='outside',
        textfont=dict(size=12),  # Set consistent text size
        hovertemplate='Year: %{x}<br>Medalhas de Ouro: %{customdata:.0f}<br>Proporção de Ouros: %{y:.2f}<extra></extra>',
    ))

    # Update layout for the Marimekko chart
    fig.update_layout(
        title=f'Proporção de Medalhas - {country}',
        barmode='stack',
        xaxis=dict(
            title='Ano',
            tickmode='array',
            tickvals=medal_pivot['x'],
            ticktext=unique_years,
            showgrid=False,  # Hide vertical grid lines
            range=[-0.5 * padding, len(unique_years) * (bar_width + padding) - 0.5 * padding]  # Set x-axis range to fit all bars
        ),
        yaxis=dict(
            title='Proporção de Medalhas',
            tickformat='.0%',
            gridcolor='lightgray',
        range=[0, 1.1]  # Set horizontal grid lines to light gray
        ),
        paper_bgcolor='rgba(0,0,0,0)',  # Entire figure background
        plot_bgcolor='rgba(0,0,0,0)',
        width=1500,  # Set figure width
        height=600,  # Set figure height
    )
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
                    animation_frame='Ano',
                    color_continuous_scale=px.colors.sequential.Blues)  # Escolha uma escala de cores adequada

# Atualizar o layout para definir a cor dos países sem medalhas
fig.update_traces(marker=dict(line=dict(color='rgb(255,255,255)', width=1)))  # Borda branca
fig.update_traces(marker_line_color='gray', marker_line_width=0.5)  # Borda cinza
fig.update_traces(marker_opacity=0.8)  # Opacidade dos países com medalhas


# Exibir o gráfico de cloropleth
st.plotly_chart(fig)

# Ordenar a tabela de quantidade total de medalhas por país pelo ano
medal_count_sorted = medal_count.sort_values(by='Ano')

# Botões para ordenação da tabela de quantidade total de medalhas por país
st.subheader(f"Quantidade Total de Medalhas por País ({season})")
order_by_medals_button = st.checkbox('Ordenar por número de medalhas (Países)', key='order_by_medals_button')
order_by_year_button = st.checkbox('Ordenar por ano (Países)', key='order_by_year_button')

# Ordenar a tabela conforme os botões selecionados
if order_by_medals_button:
    medal_count_sorted = medal_count_sorted.sort_values(by='total_medals', ascending=False)

if order_by_year_button:
    medal_count_sorted = medal_count_sorted.sort_values(by='Ano')

# Adicionando a coluna "Temporada" à tabela de quantidade total de medalhas por país
medal_count_sorted_with_season = medal_count_sorted.copy()
medal_count_sorted_with_season['Temporada'] = season

# Tabela de quantidade total de medalhas por país
st.write(medal_count_sorted_with_season.rename(columns={'total_medals': 'Quantidade Medalhas', 'Ano': 'Ano'}).astype({'Ano': int}))


# --------------------------------------------------------
# Botões para ordenação da tabela de detalhes das medalhas
st.subheader("Detalhes de Medalhas por País, Ano, Esporte e Gênero")

order_by_medals_button_detailed = st.checkbox('Ordenar por número de medalhas (Detalhes)', key='order_by_medals_button_detailed')
order_by_year_button_detailed = st.checkbox('Ordenar por ano (Detalhes)', key='order_by_year_button_detailed')

# Ordenar a tabela conforme os botões selecionados
detailed_medal_info_sorted = detailed_medal_info
if order_by_medals_button_detailed:
    detailed_medal_info_sorted = detailed_medal_info_sorted.sort_values(by='count', ascending=False)

if order_by_year_button_detailed:
    detailed_medal_info_sorted = detailed_medal_info_sorted.sort_values(by='Ano')

# Adicionando a coluna "Temporada" à tabela de detalhes das medalhas
detailed_medal_info_sorted_with_season = detailed_medal_info_sorted.copy()
detailed_medal_info_sorted_with_season['Temporada'] = season

# Tabela de detalhes das medalhas por país, ano, esporte e gênero
st.write(detailed_medal_info_sorted_with_season.rename(columns={'count': 'Quantidade Medalhas', 'Ano': 'Ano'}).astype({'Ano': int}))

st.subheader('Evolução das medalhas por país')
# Seleção de país pelo usuário
selected_country2 = st.selectbox(
    "Selecione um país:",
    sorted(df_unique['NOC'].unique().tolist()),
    index=0
)

filtered_df2 = filter_data(season, gender)
filtered_df2 = filtered_df2[filtered_df2['NOC'] == selected_country2]

# Criando o gráfico de barras
fig = plot_marimekko(filtered_df2, selected_country2)

# Exibir o gráfico de barras
st.plotly_chart(fig)
