import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import plotly.express as px
import os

def load_data():
    df_freq = pd.read_csv('cell_frequency_analysis.csv')
    
    df_stats = pd.read_csv('statistical_analysis.csv')
    
    df_base_raw = pd.read_csv('melanoma_miraclib_baseline_data.csv')
    
    df_project = df_base_raw.groupby('project').agg(
        total_samples=('sample_id', 'count'),
        unique_subjects=('subject_id', 'nunique'),
        responders=('response', lambda x: (x == 'yes').sum()),
        non_responders=('response', lambda x: (x == 'no').sum()),
        males=('sex', lambda x: (x == 'M').sum()),
        females=('sex', lambda x: (x == 'F').sum())
    ).reset_index()
    
    return df_freq, df_stats, df_project

df_f, df_s, df_p = load_data()

#dashboard
app = dash.Dash(__name__)

app.layout = html.Div(style={'padding': '40px', 'backgroundColor': '#f4f7f6'}, children=[
    html.H1("Clinical Trial: Predictive Analytics Dashboard", 
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '30px'}),

    html.Div([
        html.H3("Baseline Project Enrollment Summary"),
        dash_table.DataTable(
            data=df_p.to_dict('records'),
            columns=[{"name": i.replace('_', ' ').title(), "id": i} for i in df_p.columns],
            style_header={'backgroundColor': '#34495e', 'color': 'white', 'fontWeight': 'bold'},
            style_cell={'textAlign': 'center', 'fontFamily': 'sans-serif'},
        )
    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '30px'}),

    html.Div([
        html.H3("Statistical Predictors of Response"),
        html.P("Significant differences identified using Mann-Whitney U testing (p < 0.05)."),
        dash_table.DataTable(
            data=df_s.to_dict('records'),
            columns=[{"name": i.replace('_', ' ').title(), "id": i} for i in df_s.columns],
            style_data_conditional=[
                {
                    'if': {'filter_query': '{significant} eq "Yes"'},
                    'backgroundColor': '#dff0d8',
                    'color': '#3c763d',
                    'fontWeight': 'bold'
                }
            ],
            style_header={'backgroundColor': '#34495e', 'color': 'white', 'fontWeight': 'bold'},
            style_cell={'textAlign': 'center', 'padding': '10px'}
        )
    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '30px'}),

    html.Div([
        html.H3("Population Frequency Distribution"),
        html.Label("Select Cell Population:"),
        dcc.Dropdown(
            id='pop-dropdown',
            options=[{'label': c.replace('_', ' ').title(), 'value': c} for c in df_f['population'].unique()],
            value='cd4_t_cell',
            style={'width': '300px', 'marginBottom': '20px'}
        ),
        dcc.Graph(id='cell-boxplot')
    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px'})
])

@app.callback(
    Output('cell-boxplot', 'figure'),
    [Input('pop-dropdown', 'value')]
)
def update_graph(selected_pop):
    filtered = df_f[df_f['population'] == selected_pop]
    
    fig = px.box(
        filtered, x='population', y='percentage', color='response',
        points="outliers",
        color_discrete_map={'yes': '#27ae60', 'no': '#e74c3c'},
        title=f"Baseline Frequency: {selected_pop.replace('_', ' ').title()}",
        labels={'percentage': 'Frequency (%)', 'response': 'Responded?'}
    )
    fig.update_layout(template='plotly_white')
    return fig

if __name__ == '__main__':
    app.run(debug=True)