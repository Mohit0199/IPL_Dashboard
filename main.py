import dash
from dash import dcc, dash_table, html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd


external_stylesheets = [
    {
        "href": "https://stackpath.bootstrapcdn.com/bootswatch/4.1.3/css/bootstrap.min.css",
        "rel": "stylesheet",
        "integrity": "sha384.MCw98/SF-nGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm82iuXoaPkFOJwJ8ERdknl.PMO",
        "crossorigin": "anonymous",
    }
]

df_matches = pd.read_csv('ipl-matches.csv')
seasons_df = pd.read_csv('IPL_all_balls_2008_2022.csv')
seasons_df = pd.merge(seasons_df, df_matches[['ID', 'Venue']], on='ID', how='left')


all_seasons = ['All'] + df_matches['Season'].unique().tolist()

teams = pd.concat([df_matches['Team1'], df_matches['Team2']]).unique().tolist()
all_teams = ['All'] + pd.concat([df_matches['Team1'], df_matches['Team2']]).unique().tolist()

all_players = pd.concat([df_matches['Player_of_Match'], seasons_df['batter'], seasons_df['bowler'], seasons_df['non-striker']]).unique()
all_players = sorted([player for player in all_players if pd.notna(player)])

all_batsman = sorted(seasons_df['batter'].unique())
all_bowler = sorted(seasons_df['bowler'].unique())

seasons = {name: group for name, group in seasons_df.groupby('Season')}


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
    html.H1("IPL Dashboard", style={'color': '#fff', 'text-align': 'center'}),
    html.H2('Explore and analyze the comprehensive data of all IPL matches from 2008 to 2022.',
            style={'color': '#fff', 'text-align': 'center'}),
    html.Div([
        dcc.Markdown(
            """
            ### Welcome to the IPL Dashboard! 🏏

            Select your preferred season(s) and team(s) from the dropdown menus above to uncover exciting match details.
            """,
            style={'color': '#11235A','fontSize': 18}
        ),

        dcc.Dropdown(
            id='season-dropdown',
            options=[{'label': season, 'value': season} for season in all_seasons],
            multi=True,
            placeholder="Select a season",
            style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}
        ),

        dcc.Dropdown(
            id='team-dropdown',
            options=[{'label': team, 'value': team} for team in all_teams],
            multi=True,
            placeholder="Select team(s)",
            style={'width': '48%', 'display': 'inline-block', 'padding': '10px', 'float': 'right'}
        )
    ], className='row', style={'margin-top': '20px','background-color': '#BFCCB5'}),

    html.Div([
        html.Div(id='table'),

        # Message for no info available
        html.Div(id='info-message', style={'margin-top': '10px', 'color': 'red', 'fontSize': 20, 'font-family': 'Arial'}),
    ], className='row', style={'margin-top': '20px', 'background-color': '#BFCCB5'}),
    
    html.Div([
        dcc.Markdown(
            """
            ### Explore Batsman Performance Across Seasons

            Choose a player from the dropdown menu above to view their runs scored in each IPL season.
            """,
            style={'color': '#11235A','fontSize': 18}
        ),

        dcc.Dropdown(
            id='batsman-dropdown',
            options=[{'label': player, 'value': player} for player in all_players],
            multi=False,
            placeholder="Select a player",
            style={'width': '48%', 'padding': '10px', 'display': 'inline-block'}
        ),

        html.Div(id='batsman-table'),
        html.Div(id='batsman-chart')
    ], className='row', style={'margin-top': '20px','background-color': '#BFCCB5'}),
    
    html.Div([
        dcc.Markdown(
            """
            ### Explore Bowler Performance Across Seasons

            Choose a bowler from the dropdown menu above to view their bowling performance in each IPL season.

            """,
            style={'color': '#11235A','fontSize': 18}
        ),

        dcc.Dropdown(
            id='bowler-dropdown',
            options=[{'label': bowler, 'value': bowler} for bowler in all_bowler],
            multi=False,
            placeholder="Select a player",
            style={'width': '48%', 'padding': '10px', 'display': 'inline-block'}
        ),

        html.Div(id='bowler-table'),
        html.Div(id='bowler-chart')
    ], className='row', style={'margin-top': '20px','background-color': '#BFCCB5'}),

    html.Div([
        dcc.Markdown(
            """
            ### Explore Team Performance Across Seasons

            Choose a team from the dropdown menu above to view their performance in each IPL season.

            """,
            style={'color': '#11235A','fontSize': 18}
        ),

        dcc.Dropdown(
        id='team-performance-dropdown',
        options=[{'label': team, 'value': team} for team in teams],
        multi=False,
        placeholder="Select a team",
        style={'width': '48%', 'padding': '10px', 'display': 'inline-block'}
        ),

        html.Div(id='team-performance-heatmap')
    ], className='row', style={'margin-top': '20px','background-color': '#BFCCB5'})

     
], className='container')

app.title = "IPL Dashboard"

@app.callback(
    [Output('table','children'),
     Output('info-message', 'children')],
     [Input('season-dropdown', 'value'),
      Input('team-dropdown', 'value')]
)
def update_matches_table(selected_season, selected_teams):
    if selected_season is None or selected_teams is None:
        # If no season or team is selected, return empty table and no info message
        return [],''

    if 'All' in selected_season and 'All' in selected_teams:
        # If 'All' is selected for both season and team, display the entire dataframe
        filtered_matches = df_matches
    elif 'All' in selected_season:
        # If 'All' is selected for season, display all matches for selected team(s)
        filtered_matches = df_matches[
            (df_matches['Team1'].isin(selected_teams) | df_matches['Team2'].isin(selected_teams))
        ]
    elif 'All' in selected_teams:
        # If 'All' is selected for teams, display all matches for selected season(s)
        filtered_matches = df_matches[
            (df_matches['Season'].isin(selected_season))
        ]
    else:
        # Filter data based on selected season and team(s)
        filtered_matches = df_matches[
            (df_matches['Season'].isin(selected_season)) &
            (df_matches['Team1'].isin(selected_teams) | df_matches['Team2'].isin(selected_teams))
        ]

    # Convert DataFrame to dictionary for DataTable
    matches_data = filtered_matches.to_dict('records')

    table = dash_table.DataTable(
                columns=[{'name': col, 'id': col} for col in df_matches.columns],
                data=matches_data,
                page_size=10,
                style_header={'backgroundColor': '#383c3d', 'color': '#edf3f5'},
                style_data={'backgroundColor': '#ecf0f1'},
                style_cell={'fontSize': 16, 'font-family': 'Arial'},
                style_table={'maxHeight': '400px', 'overflowY': 'scroll'}
            )

    message = ''
    
    if  'All' not in selected_season:
        teams_played_in_season = set(
        set(df_matches[df_matches['Season'].isin(selected_season)]['Team1'])
        | set(df_matches[df_matches['Season'].isin(selected_season)]['Team2'])
        )
        teams_not_played = [team for team in selected_teams if team not in teams_played_in_season]

        if teams_not_played:
            # If any selected team did not play in the selected season, set the message
            message = f'The following team(s) did not play in the selected season: {", ".join(teams_not_played)}.'

    return table, message


@app.callback(
    [Output('batsman-table','children'),
     Output('batsman-chart', 'children')],
    Input('batsman-dropdown', 'value')
)
def update_batsman_table(selected_player):
    if selected_player is None:
        return [],''
    
    pivot_df = pd.DataFrame()

    for season, season_df in seasons.items():
        player_season_data = {
            'Season': season,
            'Match_played': season_df[(season_df['batter']==selected_player) | (season_df['bowler']==selected_player)]['ID'].nunique(),
            '1s': season_df[(season_df['batter'] == selected_player) & (season_df['batsman_run'] == 1)]['batsman_run'].count(),
            '2s': season_df[(season_df['batter'] == selected_player) & (season_df['batsman_run'] == 2)]['batsman_run'].count(),
            '3s': season_df[(season_df['batter'] == selected_player) & (season_df['batsman_run'] == 3)]['batsman_run'].count(),
            '4s': season_df[(season_df['batter'] == selected_player) & (season_df['batsman_run'] == 4)]['batsman_run'].count(),
            '6s': season_df[(season_df['batter'] == selected_player) & (season_df['batsman_run'] == 6)]['batsman_run'].count(),
            'Highest Runs': season_df[(season_df['batter']==selected_player)].groupby('ID')['batsman_run'].sum().max(),
            'Runs': season_df[(season_df['batter'] == selected_player)]['batsman_run'].sum(),
        }
        pivot_df = pd.concat([pivot_df, pd.DataFrame([player_season_data])])
    total_row = {
    'Season': 'All Season',
    'Match_played': pivot_df['Match_played'].sum(),
    '1s': pivot_df['1s'].sum(),
    '2s': pivot_df['2s'].sum(),
    '3s': pivot_df['3s'].sum(),
    '4s': pivot_df['4s'].sum(),
    '6s': pivot_df['6s'].sum(),
    'Highest Runs': pivot_df['Highest Runs'].max(),
    'Runs': pivot_df['Runs'].sum(),
    }
    pivot_df = pd.concat([pivot_df, pd.DataFrame([total_row])])
    
    pivot_data = pivot_df.to_dict('records')

    table = dash_table.DataTable(
            columns=[
                {'name': 'Season', 'id': 'Season'},
                {'name': 'Matches Played', 'id': 'Match_played'},
                {'name': '1s', 'id': '1s'},
                {'name': '2s', 'id': '2s'},
                {'name': '3s', 'id': '3s'},
                {'name': '4s', 'id': '4s'},
                {'name': '6s', 'id': '6s'},
                {'name': 'Highest Runs', 'id': 'Highest Runs'},
                {'name': 'Runs', 'id': 'Runs'},
            ],
            data=pivot_data,
            style_header={'backgroundColor': '#383c3d', 'color': '#edf3f5'},
            style_data={'backgroundColor': '#ecf0f1'},
            style_cell={
                'fontSize': 15,
                'font-family': 'Arial',
                'width': '10px',
                'whiteSpace': 'normal',
                'textAlign': 'center'
                },
            )
    
    selected_player_data = seasons_df[seasons_df['batter'] == selected_player]
    total_runs_per_venue = selected_player_data.groupby('Venue')['batsman_run'].sum().reset_index()

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=total_runs_per_venue['Venue'],
            y=total_runs_per_venue['batsman_run'],
            textposition='auto',
            marker=dict(color='blue')
        )
    )

    fig.update_layout(
        title=f"{selected_player}'s Total Runs at Each Venue",
        xaxis_title='Venue',
        yaxis_title='Total Runs',
        height=1000,
        width=1500,
        template='plotly_dark'
    )

    figure = dcc.Graph(
        id='venue-total-runs-chart',
        figure = fig
    )

    return [dcc.Markdown(f"""{selected_player}'s All season runs""",
                         style={'color': '#191717', 'text-align': 'center','fontSize': 20, 'font-family': 'Arial'}),
            table], figure


    
    
@app.callback(
    [Output('bowler-table','children'),
     Output('bowler-chart', 'children')],
    Input('bowler-dropdown', 'value')
)
def update_bowler_table(selected_player):
    if selected_player is None:
        return [],''
    
    pivot_df = pd.DataFrame()

    for season, season_df in seasons.items():
        player_season_data = {
            'Season': season,
            'Match_played': season_df[(season_df['bowler']==selected_player) | (season_df['batter']==selected_player)]['ID'].nunique(),
            'total_wicket': season_df[(season_df['bowler'] == selected_player) &
                                      (season_df['isWicketDelivery']==1) &
                                      (season_df['kind'].isin(['caught', 'caught and bowled', 'bowled', 'lbw','stumped']))
                                    ]['ID'].count(),
            'Stumped out': season_df[(season_df['bowler'] == selected_player) &
                                     (season_df['isWicketDelivery']==1) &
                                     (season_df['kind']=='stumped')
                                    ]['ID'].count(),
            'Caught out': season_df[(season_df['bowler'] == selected_player) &
                                    (season_df['isWicketDelivery']==1) &
                                    (season_df['kind'].isin(['caught', 'caught and bowled', 'bowled']))
                                    ]['ID'].count(),
            'lbw': season_df[(season_df['bowler'] == selected_player) &
                             (season_df['isWicketDelivery']==1) &
                             (season_df['kind']=='lbw')
                            ]['ID'].count(),
            'runs_given': season_df[season_df['bowler']==selected_player]['total_run'].sum(),
            'Overs' : f"{(season_df[(season_df['bowler']==selected_player) & (season_df['ballnumber'].isin([1,2,3,4,5,6]))].groupby('overs')['ballnumber'].count().sum()) // 6}.{(season_df[(season_df['bowler']==selected_player) & (season_df['ballnumber'].isin([1,2,3,4,5,6]))].groupby('overs')['ballnumber'].count().sum()) % 6}"
        }
        pivot_df = pd.concat([pivot_df, pd.DataFrame([player_season_data])])

                  
    total_row = {
        'Season': 'All Season',
        'Match_played': pivot_df['Match_played'].sum(),
        'total_wicket': pivot_df['total_wicket'].sum(),
        'Stumped out': pivot_df['Stumped out'].sum(),
        'Caught out': pivot_df['Caught out'].sum(),
        'lbw': pivot_df['lbw'].sum(),
        'runs_given': pivot_df['runs_given'].sum(),
        'Overs': f"{(seasons_df[(seasons_df['bowler']==selected_player) & (seasons_df['ballnumber'].isin([1,2,3,4,5,6]))].groupby('overs')['ballnumber'].count().sum()) // 6}.{(seasons_df[(seasons_df['bowler']==selected_player) & (seasons_df['ballnumber'].isin([1,2,3,4,5,6]))].groupby('overs')['ballnumber'].count().sum()) % 6}"
    }

    pivot_df = pd.concat([pivot_df, pd.DataFrame([total_row])])
    
    pivot_data = pivot_df.to_dict('records')

    table = dash_table.DataTable(
            columns=[
                {'name': 'Season', 'id': 'Season'},
                {'name': 'Matches Played', 'id': 'Match_played'},
                {'name': 'Total Wicket', 'id': 'total_wicket'},
                {'name': 'Stumped Out', 'id': 'Stumped out'},
                {'name': 'Caught Out', 'id': 'Caught out'},
                {'name': 'LBW', 'id': 'lbw'}, 
                {'name': 'Runs Given', 'id': 'runs_given'},
                {'name': 'Overs', 'id': 'Overs'},
            ],
            data=pivot_data,
            style_header={'backgroundColor': '#383c3d', 'color': '#edf3f5'},
            style_data={'backgroundColor': '#ecf0f1'},
            style_cell={
                'fontSize': 15,
                'font-family': 'Arial',
                'width': '10px',
                'whiteSpace': 'normal',
                'textAlign': 'center'
                },
            )
    
    selected_player_data = seasons_df[
    (seasons_df['bowler'] == selected_player) &
    (seasons_df['isWicketDelivery'] == 1) &
    (seasons_df['kind'].isin(['caught', 'caught and bowled', 'bowled', 'lbw', 'stumped']))
]

    total_wickets_per_venue = selected_player_data.groupby('Venue').size().reset_index(name='TotalWickets')

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=total_wickets_per_venue['Venue'],
            y=total_wickets_per_venue['TotalWickets'],
            textposition='auto',
            marker=dict(color='blue')
        )
    )

    fig.update_layout(
        title=f"{selected_player}'s Total Wickets at Each Venue",
        xaxis_title='Venue',
        yaxis_title='Total Wickets',
        height=900,
        width=1500,
        template='plotly_dark'
    )

    figure = dcc.Graph(
        id='venue-total-wickets-chart',
        figure = fig
    )

    return [dcc.Markdown(f"""{selected_player}'s All season bowling performance""",
                         style={'color': '#191717', 'text-align': 'center','fontSize': 20, 'font-family': 'Arial'}),
            table], figure



@app.callback(
    Output('team-performance-heatmap', 'children'),
    [Input('team-performance-dropdown', 'value')]
)
def update_team_performance_heatmap(selected_team):
    if selected_team is None:
        return []

    team_performance_data = df_matches[(df_matches['Team1'] == selected_team) | (df_matches['Team2'] == selected_team)]
    team_performance_data.loc[:, 'Opponent'] = team_performance_data.apply(
    lambda row: row['Team2'] if row['Team1'] == selected_team else row['Team1'], axis=1)

    season_opponent_stats = (
        team_performance_data.groupby(['Season', 'Opponent'])
        .agg(TotalMatches=('ID', 'count'), TotalWins=('WinningTeam', lambda x: (x == selected_team).sum()))
        .reset_index()
    )

    fig = go.Figure()
    size_scaling_factor = 10

    for index, row in season_opponent_stats.iterrows():
        fig.add_trace(
            go.Scatter(
                x=[row['Season']],
                y=[row['Opponent']],
                mode='markers',
                marker=dict(
                    size=row['TotalMatches'] * size_scaling_factor,
                    color='green' if row['TotalWins'] > 0 else 'red',
                    opacity=0.7,
                ),
                text=f"Matches: {row['TotalMatches']}<br>Wins: {row['TotalWins']}",
                name=row['Opponent'],
                hoverinfo='text',
            )
        )

    fig.update_layout(
        title=f"Matches Played Against Each Opponent for {selected_team}",
        xaxis_title='Season',
        yaxis_title='Opponent',
        showlegend=False,
        height=700,
        width=1500,
        template='plotly_dark'
    )


    figure = dcc.Graph(
        id='team-performance',
        figure = fig
    )
    return figure



if __name__ == "__main__":
    app.run_server(debug=True)
