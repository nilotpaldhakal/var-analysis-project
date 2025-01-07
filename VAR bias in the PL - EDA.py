import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# Load dataset
FILE_PATH = r'C:\\Users\\nilot\\OneDrive\\Documents\\KU\\IV—I\\COMP 482 (Data Mining)\\Project\\VAR in PL\\VAR_Team_Stats.csv'

# Color Palette
COLORS = {
    'background': '#F4F6F9',
    'card_background': '#FFFFFF',
    'primary': '#3498db',
    'secondary': '#2ecc71',
    'text': '#2c3e50',
    'accent': '#e74c3c'
}

class VARBiasAnalyzer:
    def __init__(self, file_path):
        """
        Initialize VAR Bias Analysis
        """
        self.df = pd.read_csv(file_path)
        self._preprocess_data()
    
    def _preprocess_data(self):
        """
        Preprocess and clean the dataset
        """
        numeric_columns = [
            'Overturns', 'Leading to goals for', 'Disallowed goals for', 
            'Leading to goals against', 'Disallowed goals against', 
            'Net goal score', 'Subjective decisions for', 
            'Subjective decisions against', 'Net subjective score'
        ]
        
        for col in numeric_columns:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        self.df.fillna(0, inplace=True)
    
    def calculate_comprehensive_bias_score(self):
        """
        Calculate a multi-dimensional bias score
        """
        def bias_score(row):
            goals_bias = (row['Leading to goals for'] - row['Disallowed goals for']) - \
                         (row['Leading to goals against'] - row['Disallowed goals against'])
            
            subjective_bias = row['Subjective decisions for'] - row['Subjective decisions against']
            net_goal_impact = row['Net goal score']
            overturns_impact = row['Overturns']
            
            bias_score = (
                0.3 * (goals_bias / self.df['Net goal score'].max()) +
                0.2 * (subjective_bias / self.df['Subjective decisions for'].max()) +
                0.3 * (net_goal_impact / abs(self.df['Net goal score']).max()) +
                0.2 * (overturns_impact / self.df['Overturns'].max())
            )
            
            return bias_score
        
        return self.df.apply(bias_score, axis=1)



# Initialize the analyzer
var_analyzer = VARBiasAnalyzer(FILE_PATH)

# Calculate bias scores
var_analyzer.df['Bias Score'] = var_analyzer.calculate_comprehensive_bias_score()

# Create Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                background-color: ''' + COLORS['background'] + ''';
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .card {
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 20px;
                border-radius: 10px;
                overflow: hidden;
            }
            .nav-tabs .nav-link {
                color: ''' + COLORS['text'] + ''';
            }
            .nav-tabs .nav-link.active {
                background-color: ''' + COLORS['primary'] + ''';
                color: white !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# App layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col(html.H1("VAR Bias Analysis Dashboard", 
                         style={
                             'color': COLORS['text'], 
                             'textAlign': 'center', 
                             'marginBottom': '30px',
                             'fontWeight': 'bold'
                         }), 
                className="mb-4")
    ]),
    
    # Team Dropdown
    dbc.Row([
        dbc.Col([
            html.Label("Select Team:", style={'color': COLORS['text']}),
            dcc.Dropdown(
                id='team-dropdown',
                options=[{'label': team, 'value': team} for team in var_analyzer.df['Team']],
                value='Arsenal',
                placeholder="Select a team",
                style={
                    'backgroundColor': COLORS['card_background'],
                    'color': COLORS['text']
                }
            )
        ], width=6, className="mx-auto")
    ], className="mb-4"),
    
    # Tabs with improved styling
    dbc.Tabs([
        # Overall Analysis Tab
        dbc.Tab(label='Overall Analysis', children=[
            dbc.Row([
                # Bias Score Ranking
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("VAR Bias Scores"),
                        dbc.CardBody(dcc.Graph(id='overall-bias-ranking'))
                    ], className="card")
                ], width=12),
                
                # Correlation Heatmap
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Correlation of VAR Metrics"),
                        dbc.CardBody(dcc.Graph(id='correlation-heatmap'))
                    ], className="card")
                ], width=6),
                
                # Subjective Decisions Scatter
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Subjective Decisions Comparison"),
                        dbc.CardBody(dcc.Graph(id='subjective-decisions-scatter'))
                    ], className="card")
                ], width=6),
                
                # Box Plot of Net Goal Scores
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Net Goal Scores Distribution"),
                        dbc.CardBody(dcc.Graph(id='net-goal-score-boxplot'))
                    ], className="card")
                ], width=12)
            ])
        ]),
        
        # Team-Specific Tab
        dbc.Tab(label='Team-Specific Analysis', children=[
            dbc.Row([
                # Team Metrics Cards
                dbc.Col([
                    html.Div(id='team-metrics-cards', style={
                        'display': 'flex', 
                        'justifyContent': 'space-around',
                        'marginBottom': '20px'
                    })
                ], width=12),
                
                # Team Detailed Visualizations
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("VAR Metrics Breakdown"),
                        dbc.CardBody(dcc.Graph(id='team-var-metrics-breakdown'))
                    ], className="card")
                ], width=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Subjective Decisions"),
                        dbc.CardBody(dcc.Graph(id='team-subjective-decisions-pie'))
                    ], className="card")
                ], width=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Goals Impact"),
                        dbc.CardBody(dcc.Graph(id='team-goals-impact-chart'))
                    ], className="card")
                ], width=12)
            ])
        ])
    ])
], fluid=True)


# Callback for overall visualizations
@app.callback(
    [
        Output('overall-bias-ranking', 'figure'),
        Output('correlation-heatmap', 'figure'),
        Output('subjective-decisions-scatter', 'figure'),
        Output('net-goal-score-boxplot', 'figure')
    ],
    [Input('team-dropdown', 'value')]
)
def update_overall_visualizations(selected_team):
    # Bias Score Ranking
    overall_bias_fig = px.bar(
        var_analyzer.df.sort_values('Bias Score', ascending=False), 
        x='Team', 
        y='Bias Score',
        title='VAR Bias Scores Across Teams',
        color='Bias Score',
        color_continuous_scale='RdYlGn',
        template='plotly_white'
    )
    overall_bias_fig.update_layout(
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['background'],
        font_color=COLORS['text']
    )
    
    # Correlation Heatmap
    corr_matrix = var_analyzer.df[
        ['Overturns', 'Leading to goals for', 'Disallowed goals for', 
         'Net goal score', 'Subjective decisions for']
    ].corr()
    
    correlation_fig = px.imshow(
        corr_matrix, 
        title='Correlation of VAR Metrics',
        color_continuous_scale='RdBu_r',
        template='plotly_white'
    )
    correlation_fig.update_layout(
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['background'],
        font_color=COLORS['text']
    )
    
    # Subjective Decisions Scatter
    subjective_scatter = px.scatter(
        var_analyzer.df, 
        x='Subjective decisions for', 
        y='Subjective decisions against',
        color='Team',
        title='Subjective Decisions Comparison',
        hover_data=['Team', 'Subjective decisions for', 'Subjective decisions against'],
        template='plotly_white'
    )
    subjective_scatter.update_layout(
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['background'],
        font_color=COLORS['text']
    )
    
    # Net Goal Score Box Plot
    net_goal_boxplot = px.box(
        var_analyzer.df, 
        x='Team', 
        y='Net goal score',
        title='Distribution of Net Goal Scores',
        color='Team',
        template='plotly_white'
    )
    net_goal_boxplot.update_layout(
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['background'],
        font_color=COLORS['text']
    )
    
    return overall_bias_fig, correlation_fig, subjective_scatter, net_goal_boxplot

# Callback for team-specific updates
@app.callback(
    [
        Output('team-metrics-cards', 'children'),
        Output('team-var-metrics-breakdown', 'figure'),
        Output('team-subjective-decisions-pie', 'figure'),
        Output('team-goals-impact-chart', 'figure')
    ],
    [Input('team-dropdown', 'value')]
)
def update_team_section(selected_team):
    if not selected_team:
        return (
            [],
            {},
            {},
            {}
        )
    
    # Get team-specific data
    team_data = var_analyzer.df[var_analyzer.df['Team'] == selected_team].iloc[0]
    
    # Metrics Cards
    metrics_cards = [
        dbc.Card([
            dbc.CardHeader("Overturns"),
            dbc.CardBody(html.H4(f"{team_data['Overturns']}", className="card-title", style={'color': COLORS['primary']}))
        ], className="card"),
        dbc.Card([
            dbc.CardHeader("Net Goal Score"),
            dbc.CardBody(html.H4(f"{team_data['Net goal score']}", className="card-title", style={'color': COLORS['primary']}))
        ], className="card"),
        dbc.Card([
            dbc.CardHeader("Subjective Decisions"),
            dbc.CardBody(html.H4(f"{team_data['Subjective decisions for']} - {team_data['Subjective decisions against']}", 
                                  className="card-title", style={'color': COLORS['primary']}))
        ], className="card")
    ]
    
    # Team VAR Metrics Breakdown
    var_metrics_breakdown = {
        'data':
            [
                go.Bar(
                    x=['Leading to goals for', 'Leading to goals against', 'Disallowed goals for', 'Disallowed goals against'],
                    y=[
                        team_data['Leading to goals for'],
                        team_data['Leading to goals against'],
                        team_data['Disallowed goals for'],
                        team_data['Disallowed goals against']
                    ],
                    marker_color=COLORS['secondary']
                )
            ],
            'layout': go.Layout(
                title=f'VAR Metrics Breakdown for {selected_team}',
                xaxis={'title': 'Metrics'},
                yaxis={'title': 'Count'},
                plot_bgcolor=COLORS['background'],
                paper_bgcolor=COLORS['background'],
                font_color=COLORS['text']
            )
        }
    
    # Team Subjective Decisions Pie Chart
    subjective_decisions_pie = {
        'data': [
            go.Pie(
                labels=['For', 'Against'],
                values=[team_data['Subjective decisions for'], team_data['Subjective decisions against']],
                hole=.3,
                marker=dict(colors=[COLORS['primary'], COLORS['accent']])
            )
        ],
        'layout': go.Layout(
            title=f'Subjective Decisions for {selected_team}',
            plot_bgcolor=COLORS['background'],
            paper_bgcolor=COLORS['background'],
            font_color=COLORS['text']
        )
    }
    
    # Goals Impact Chart
    goals_impact_chart = {
        'data': [
            go.Bar(
                x=['Goals For', 'Goals Against'],
                y=[
                    team_data['Leading to goals for'],
                    team_data['Leading to goals against']
                ],
                marker_color=COLORS['secondary']
            )
        ],
        'layout': go.Layout(
            title=f'Goals Impact for {selected_team}',
            xaxis={'title': 'Goals'},
            yaxis={'title': 'Count'},
            plot_bgcolor=COLORS['background'],
            paper_bgcolor=COLORS['background'],
            font_color=COLORS['text']
        )
    }
    
    return metrics_cards, var_metrics_breakdown, subjective_decisions_pie, goals_impact_chart


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)