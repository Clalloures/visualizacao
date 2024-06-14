import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide")
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

# Seleção de país pelo usuário
selected_country = st.selectbox(
    "Selecione um país:",
    sorted(df_unique['NOC'].unique().tolist()),
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
fig = plot_marimekko(filtered_df, selected_country)

# Exibir o gráfico de barras
st.plotly_chart(fig)

# Tabela de contagem de medalhas
st.subheader("Contagem de Medalhas por Ano")

# Botões para ordenar a tabela
sort_by = st.selectbox("Ordenar por:", ["Ano", "Total", "Ouro", "Prata", "Bronze", "País"])

# Ordenar a tabela de acordo com a seleção do usuário
if sort_by == "Ano":
    medal_count_sorted = medal_count.sort_values(by=['Ano'])
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
st.write(medal_count_sorted.rename(columns={'total_medals': 'Total', 'gold_medals': 'Ouro', 'silver_medals': 'Prata', 'bronze_medals': 'Bronze'}).astype({'Ano': str}))

# Exibir detalhes apenas se um país específico for selecionado
if selected_country != "Todos":
    st.subheader(f"Detalhes das Medalhas para {selected_country}")
    st.write(filtered_df[['Ano', 'Medalha']].groupby('Ano').count().rename(columns={'Medalha': 'Total de Medalhas'}).astype({'Total de Medalhas': int}))
