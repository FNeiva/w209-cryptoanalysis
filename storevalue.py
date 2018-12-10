import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv(
    'crypto10-markets-am.csv')

app.layout = html.Div(children = [
    html.H1(children='How volatile are crypto prices?'),

    
    html.Div(children='''
        % Change in Prices by Day for Top 10 Cryptocurrencies by Market Cap (2013-2018)
        
        Hover over the data points to see more details.
        You can click on the currency names on the legends to add/eliminate them from the graph.
    '''),

    # graph 1
    dcc.Graph(
        id='change',
        config = {
            'displaylogo': False
        },
        figure={'data': [go.Scatter(
            x = df[df['name'] == i].date,
            y = df[df['name'] == i]['change%'],
            name=i
        )
        for i in df.name.unique()],

                
                'layout': go.Layout(
                xaxis={'type': 'date', 'title': 'Date'},
                yaxis={'type': 'linear', 'title': '% Change in Day', 'tickformat': ',.000001%'}, 
                margin={'l': 100, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest')

        }
        ),
    
    # graph 2
    dcc.Graph(
        id='summary',
        config = {
            'displaylogo': False},
        figure={'data': 
                [dict(type = 'scatter',
                      x = df['name'],
                      y = df['change%'],
                      mode = 'markers',
                      transforms = [dict(
                          type = 'aggregate',
                          groups = df['name'].unique(),
                          aggregations = [dict(target = 'y', func = 'count', enabled = True),]
                      )]
                     )]

               }
        ),
])

if __name__ == '__main__':
    app.run_server(debug=True)
