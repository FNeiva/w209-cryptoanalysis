import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.tools as tools
from dash.dependencies import Input, Output, State
from dateutil.parser import parse
import math
from flask_caching import Cache
from datetime import datetime
import json

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#app = dash.Dash(__name__)

cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

df_fees = pd.read_csv('avg_transaction_fee.csv')
df_times = pd.read_csv('block_times.csv')
df_fees['date'] = pd.to_datetime(df_fees['date'],format='%Y/%m/%d')
df_times['date'] = pd.to_datetime(df_times['date'],format='%Y/%m/%d')

min_date = min(df_fees.min()['date'],df_times.min()['date'])
max_date = max(df_fees.max()['date'],df_times.max()['date'])

cryptos = {'btc':{'color':'#e41a1c'},
           'eth':{'color':'#377eb8'},
           'bch':{'color':'#4daf4a'},
           'ltc':{'color':'#984ea3'},
           'xmr':{'color':'#ff7f00'},
           'dash':{'color':'#ffff33'},
           'zec':{'color':'#a65628'}}

def build_plots(height=600,width=1400,initial_date=None,end_date=None,zoom=False):
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

    max_fee = 0
    max_time = 0
    for i in cryptos:
        mean_time = df_times_plot[i].mean()
        mean_fee = df_fees_plot[i].mean()
        if mean_time > max_time:
            max_time = mean_time
        if mean_fee > max_fee:
            max_fee = mean_fee
        traces.append(go.Scatter({'x':df_times_series['date'],
                             'y':df_times_series[i],
                             #'text':i.upper(),
                             'name':i.upper(),
                             'legendgroup':i.upper(),
                             'xaxis':'x1',
                             'yaxis':'y3',
                             'line':{'color':cryptos[i]['color']},
                             'showlegend':False}))
        traces.append(go.Scatter({'x':[mean_time],
                             'y':[mean_fee],
                             #'text':i.upper(),
                             'name':i.upper(),
                             'legendgroup':i.upper(),
                             'mode':'markers',
                             'opacity':1.0,
                             'marker':{'size':15,'color':cryptos[i]['color'],'line':{'width':0.5,'color':'black'}},
                             'xaxis':'x2',
                             'yaxis':'y2'}))
        traces.append(go.Scatter({'x':df_fees_series['date'],
                             'y':df_fees_series[i],
                             #'text':i.upper(),
                             'name':i.upper(),
                             'legendgroup':i.upper(),
                             'xaxis':'x1',
                             'yaxis':'y1',
                             'line':{'color':cryptos[i]['color']},
                             'showlegend':False}))

    range_y2 = max_fee*1.1
    range_x2 = max_time*1.1

    layout = go.Layout(
        width=width,
        height=height,
        hovermode='closest',
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
            range=[0,range_x2],
            anchor='y2',
            title='Average Block Times in Minutes'
        ),
        yaxis2=dict(
            domain=[0, 1],
            range=[0,range_y2],
            anchor='x2',
            title='Average Transaction Fees in USD'
        ),
        yaxis3=dict(
            domain=[0.55, 1],
            anchor='x1',
            title='Average Block Times in Minutes'
        ),
        images= [dict(
                  source= "/assets/fastcheap_back.png",
                  xref= "x2",
                  yref= "y2",
                  yanchor="bottom",
                  x= 0,
                  y= 0,
                  sizex=range_x2,
                  sizey=range_y2,
                  sizing= "fill",
                  opacity= 0.7,
                  layer= "below")]
    )

    return go.Figure(data=traces,layout=layout)

initial_figure = build_plots()

app.layout = html.Div([dcc.Markdown('''
#### Bitcoin Booms and Busts: Fast and Cheap Transactions Visualization

The visualization below displays data on the premise of cryptocurrencies being able to perform fast and cheap transactions. On the left side,
you can visualize time series on historical data for block times (the amount of time it takes for a transaction to show up on a block, thus
being confirmed) and the fee charged for that transaction. On the right side, you can view a scatterplot where the positioning of each
cryptocurrency is relative to the historical performance of that currency in both time and cost.

- Drag in any time series to zoom in. The right panel will reflect just the period of time selected.
- Double-click anywhere to undo the zoom and return to the original.
- Click a cryptocurrency in the legend to remove its data from the plot.
- Double-click a cryptocurrency in the legend to remove every other cryptocurrency and keep only the clicked one.
'''),
        html.Div([
            html.Div([
                html.Div([dcc.DatePickerRange(
                    id='date_range_picker',
                    display_format='MMM Do, YYYY',
                    min_date_allowed=min_date,
                    max_date_allowed=max_date,
                    initial_visible_month=max_date,
                    start_date=min_date,
                    end_date=max_date
                )],className='one-third.column')]
            ,className='row',style={'columnCount':2}),
            html.Div([
                html.Div([dcc.Graph(
                    id='fastandcheap',
                    figure=initial_figure,
                    config={
                        'displayModeBar': False
                    }
                )],className='one.column')]
            ,className='row'),
            html.Div(id="relayoutDates")
        ])
    ]
)

@app.callback(
    Output('fastandcheap', 'figure'),
    [Input('date_range_picker', 'start_date'),
     Input('date_range_picker', 'end_date')])
def display_selected_data(start_date,end_date):
    if ((start_date == str(min_date.date())) and (end_date == str(max_date.date()))):
        return initial_figure
    else:
        return build_plots(initial_date=start_date,end_date=end_date,zoom=True)

@app.callback(
    Output('date_range_picker', 'start_date'),
    [Input('fastandcheap', 'relayoutData')])
def zoom_to_start_date(relayoutData):
    if (relayoutData is None):
        return min_date
    if ('xaxis.range[0]' in relayoutData):
        initial_date = parse(relayoutData['xaxis.range[0]'])
        return initial_date
    else:
        return min_date

@app.callback(
    Output('date_range_picker', 'end_date'),
    [Input('fastandcheap', 'relayoutData')])
def zoom_to_end_date(relayoutData):
    if (relayoutData is None):
        return max_date
    if ('xaxis.range[1]' in relayoutData):
        end_date = parse(relayoutData['xaxis.range[1]'])
        return end_date
    else:
        return max_date

if __name__ == '__main__':
    app.run_server(debug=True)
