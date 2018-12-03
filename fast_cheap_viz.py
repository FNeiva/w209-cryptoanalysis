import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df_fees = pd.read_csv('avg_transaction_fee.csv')
df_times = pd.read_csv('block_times.csv')

app.layout = html.Div([
    dcc.Graph(
        id='cryptofees',
        figure={
            'data': [
                go.Scatter(
                    x=df_fees['date'],
                    y=df_fees[i],
                    text=i.upper(),
                    name=i.upper()
                ) for i in df_fees.columns[1:]
            ],
            'layout': go.Layout(
                xaxis={'title': 'Date'},
                yaxis={'title': 'Average Transaction Fees in USD'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    )
,
    dcc.Graph(
        id='cryptotimes',
        figure={
            'data': [
                go.Scatter(
                    x=df_times['date'],
                    y=df_times[i],
                    text=i.upper(),
                    name=i.upper()
                ) for i in df_times.columns[1:]
            ],
            'layout': go.Layout(
                xaxis={'title': 'Date'},
                yaxis={'title': 'Average Block Times in Minutes'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    )
,
    dcc.Graph(
        id='cryptoscatter',
        figure={
            'data': [
                go.Scatter(
                    x=[df_times[i].mean()],
                    y=[df_fees[i].mean()],
                    text=i.upper(),
                    name=i.upper(),
                    mode='markers'
                ) for i in df_times.columns[1:]
            ],
            'layout': go.Layout(
                xaxis={'title': 'Average Block Times in Minutes'},
                yaxis={'title': 'Average Transaction Fees in USD'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
