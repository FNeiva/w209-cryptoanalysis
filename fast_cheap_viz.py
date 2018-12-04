import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.tools as tools
from dash.dependencies import Input, Output
from dateutil.parser import parse
import math

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(__name__)

df_fees = pd.read_csv('avg_transaction_fee.csv')
df_times = pd.read_csv('block_times.csv')
df_fees['date'] = pd.to_datetime(df_fees['date'],format='%Y/%m/%d')
df_times['date'] = pd.to_datetime(df_times['date'],format='%Y/%m/%d')

cryptos = {'btc':{'color':'#e41a1c'},
           'eth':{'color':'#377eb8'},
           'bch':{'color':'#4daf4a'},
           'ltc':{'color':'#984ea3'},
           'xmr':{'color':'#ff7f00'},
           'dash':{'color':'#ffff33'},
           'zec':{'color':'#a65628'}}

def build_plots(height=700,width=1400,initial_date=None,end_date=None,zoom=False):
    traces = []
    if (initial_date is not None) and (end_date is not None):
        if (zoom):
            df_times_series = df_times[((df_times['date'] >= initial_date) & (df_times['date'] <= end_date))]
            df_fees_series = df_fees[((df_fees['date'] >= initial_date) & (df_fees['date'] <= end_date))]
        else:
            df_times_series = df_times
            df_fees_series = df_fees
        df_times_plot = df_times[((df_times['date'] >= initial_date) & (df_times['date'] <= end_date))]
        df_fees_plot = df_fees[((df_fees['date'] >= initial_date) & (df_fees['date'] <= end_date))]
    else:
        df_times_series = df_times
        df_fees_series = df_fees
        df_times_plot = df_times
        df_fees_plot = df_fees

    for i in cryptos:
        traces.append(go.Scatter({'x':df_times_series['date'],
                             'y':df_times_series[i],
                             'text':i.upper(),
                             'name':i.upper(),
                             'legendgroup':i.upper(),
                             'xaxis':'x1',
                             'yaxis':'y3',
                             'line':{'color':cryptos[i]['color']},
                             'showlegend':False}))
        traces.append(go.Scatter({'x':[df_times_plot[i].mean()],
                             'y':[df_fees_plot[i].mean()],
                             'text':i.upper(),
                             'name':i.upper(),
                             'legendgroup':i.upper(),
                             'mode':'markers',
                             'opacity':0.7,
                             'marker':{'size':15,'color':cryptos[i]['color'],'line':{'width':0.5,'color':'black'}},
                             'xaxis':'x2',
                             'yaxis':'y2'}))
        traces.append(go.Scatter({'x':df_fees_series['date'],
                             'y':df_fees_series[i],
                             'text':i.upper(),
                             'name':i.upper(),
                             'legendgroup':i.upper(),
                             'xaxis':'x1',
                             'yaxis':'y1',
                             'line':{'color':cryptos[i]['color']},
                             'showlegend':False}))

    layout = go.Layout(
        width=1400,
        height=700,
        xaxis=dict(
            domain=[0, 0.45],
            anchor='y1',
            title='Date'
        ),
        yaxis=dict(
            domain=[0, 0.45],
            anchor='x1',
            title='Average Transaction Fees in USD'
        ),
        xaxis2=dict(
            domain=[0.55, 1],
            anchor='y2',
            title='Average Block Times in Minutes'
        ),
        yaxis2=dict(
            #domain=[0, 1],
            anchor='x2',
            title='Average Transaction Fees in USD'
        ),
        yaxis3=dict(
            domain=[0.55, 1],
            anchor='x1',
            title='Average Block Times in Minutes'
        )
    )

    return go.Figure(data=traces,layout=layout)

app.layout = html.Div([
        dcc.Graph(
            id='fastandcheap',
            figure=build_plots()
        )
    ])

@app.callback(
    Output('fastandcheap', 'figure'),
    [Input('fastandcheap', 'relayoutData'),
     Input('fastandcheap', 'selectedData')])
def display_selected_data(relayoutData,selectedData):
    print(relayoutData)
    print(selectedData)
    if (relayoutData is not None):
        if (len(relayoutData) == 4):
            initial_date = parse(relayoutData['xaxis.range[0]'])
            end_date = parse(relayoutData['xaxis.range[1]'])
            return build_plots(initial_date=initial_date,end_date=end_date,zoom=True)
    # TODO: Selected data?
    return build_plots()

if __name__ == '__main__':
    app.run_server(debug=True)
