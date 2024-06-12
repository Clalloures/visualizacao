import pandas as pd
import plotly.graph_objects as go


def fill_in_years(df, unique_years):
    # Ensure all years are represented in the dataframe, even if there are no medals
    all_years = pd.DataFrame({'Year': unique_years})
    return pd.merge(all_years, df, on='Year', how='left').fillna(0)

def plot_marimekko(dataframe, country):
    unique_years = sorted(dataframe['Year'].unique())  # Ensure unique_years are sorted
    # Filter data for the specified country
    df_country = dataframe[dataframe['NOC'] == country]
    df_country.loc[:, 'Medal'] = df_country['Medal'].replace({'Silver': 'Prata', 'Gold': 'Ouro'})

    # Group by year and medal type and count the number of medals
    medal_counts = df_country.groupby(['Year', 'Medal']).size().reset_index(name='count')
    medal_counts = fill_in_years(medal_counts, unique_years)
    
    # Pivot the dataframe to have medal types as columns
    medal_pivot = medal_counts.pivot(index='Year', columns='Medal', values='count').fillna(0)

    # Calculate total medals per year and proportions for each medal type
    medal_pivot['total'] = medal_pivot.sum(axis=1)
    for medal in ['Ouro', 'Prata', 'Bronze']:
        medal_pivot[f'Medalhas de {medal}'] = medal_pivot[medal] / medal_pivot['total']

    # Normalize widths based on the total medals to fit the graph size
    total_medals = medal_pivot['total'].sum()
    medal_pivot['width'] = medal_pivot['total'] / total_medals

    # Compute the x positions for bars to ensure they are properly centered
    bar_width = 1 / len(unique_years)  # Adjust bar width to fit the number of years
    padding = 0.1  # Padding between bars

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
            title='Year',
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
        plot_bgcolor='rgba(0,0,0,0)'
        #width=1500,  # Set figure width
        #height=600,  # Set figure height
    )
    return fig