import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def fill_in_years(df, unique_years):
    # Get unique  
    # medals
    unique_medals = df['Medal'].unique()

    # Create a new DataFrame to store the results
    result = []

    # Iterate over unique years and medals
    for year in unique_years:
        for medal in unique_medals:
            # Check if the combination exists in the original DataFrame
            if ((df['Year'] == year) & (df['Medal'] == medal)).any():
                # If it exists, get the count
                count = df[(df['Year'] == year) & (df['Medal'] == medal)]['count'].iloc[0]
            else:
                # If it doesn't exist, set the count to 0
                count = 0
            # Append the result to the new DataFrame
            result.append({'Year': year, 'Medal': medal, 'count': count})

    # Convert the result list to a DataFrame
    result_df = pd.DataFrame(result)
    return result_df


def plot_marimekko(dataframe, country):
    unique_years = dataframe['Year'].unique()
    # Filter data for the specified country
    df_country = dataframe[dataframe['NOC'] == country]
    df_country.loc[:, 'Medal'] = df_country['Medal'].replace({'Silver': 'Prata', 'Gold': 'Ouro'})


    # Group by year and medal type and count the number of medals
    medal_counts = df_country.groupby(['Year', 'Medal']).size().reset_index(name='count')
    #medal_counts = fill_in_years(medal_counts, unique_years)
    # Pivot the dataframe to have medal types as columns
    medal_pivot = medal_counts.pivot(index='Year', columns='Medal', values='count').fillna(0)

    # Calculate total medals per year and proportions for each medal type
    medal_pivot['total'] = medal_pivot.sum(axis=1)
    for medal in ['Ouro', 'Prata', 'Bronze']:
        medal_pivot[f'Medalhas de {medal}'] = medal_pivot[medal] / medal_pivot['total']

    # Normalize widths based on the total medals to fit the graph size
    total_medals = medal_pivot['total'].sum()
    medal_pivot['width'] = medal_pivot['total'] / total_medals

    # Compute the x positions for bars to ensure they do not overlap
    x_positions = [0]  # Starting position for the first bar
    for width in medal_pivot['width'][:-1]:
        x_positions.append(x_positions[-1] + width + 0.05)  # Add small gap between bars
    medal_pivot['x'] = x_positions

    # Create the Marimekko chart with adjusted x-axis
    fig = go.Figure()

    # Add bronze trace first
    fig.add_trace(go.Bar(
        x=medal_pivot['x'],
        y=medal_pivot['Medalhas de Bronze'],
        width=medal_pivot['width'],
        base=0,
        marker=dict(color='#cd7f32'),
        name='Bronze',
        customdata=medal_pivot['total'],
        hovertemplate='Year: %{x}<br>Total de Medalhas: %{customdata}<br>Proporção de Bronzes: %{y:.2f}<extra></extra>',
    ))

    # Add silver trace second
    fig.add_trace(go.Bar(
        x=medal_pivot['x'],
        y=medal_pivot['Medalhas de Prata'],
        width=medal_pivot['width'],
        base=medal_pivot['Medalhas de Bronze'],
        marker=dict(color='#c0c0c0'),
        name='Prata',
        customdata=medal_pivot['total'],
        hovertemplate='Year: %{x}<br>Total de Medalhas: %{customdata}<br>Proporção de Pratas: %{y:.2f}<extra></extra>',
    ))

    # Add gold trace last
    fig.add_trace(go.Bar(
        x=medal_pivot['x'],
        y=medal_pivot['Medalhas de Ouro'],
        width=medal_pivot['width'],
        base=medal_pivot['Medalhas de Bronze'] + medal_pivot['Medalhas de Prata'],
        marker=dict(color='#ffd700'),
        name='Ouro',
        customdata=medal_pivot['total'],
        hovertemplate='Year: %{x}<br>Total de Medalhas: %{customdata}<br>Proporção de Ouros: %{y:.2f}<extra></extra>',
    ))

    # Update layout for the Marimekko chart
    fig.update_layout(
        title=f'Proporção de Medalhas - {country}',
        barmode='stack',
        plot_bgcolor='white',  # Set the background color to white
        xaxis=dict(
            title='Year',
            tickmode='array',
            tickvals=medal_pivot['x'],
            ticktext=medal_pivot.index.astype(str),
            showgrid=False,  # Hide vertical grid lines
        ),
        yaxis=dict(
            title='Proporção de Medalhas',
            tickformat='.0%',
            gridcolor='lightgray',  # Set horizontal grid lines to light gray
        ),
    )

    fig.show()