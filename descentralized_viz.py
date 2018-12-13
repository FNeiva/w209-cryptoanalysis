
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.graph_objs as go
import plotly.tools as tools
from dash.dependencies import Input, Output, State
import squarify
import datetime
from bisect import bisect_left

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

tm_width = 540
tm_height = 520
tm_x = 0
tm_y = 0

# color pallette for the viz
cList = ['lightcyan', 'lightblue', 'deepskyblue', 'dodgerblue', 'steelblue',
         'midnightblue']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df_acc_bins = pd.read_csv('avg_accounts_per_bin.csv')
df_acc_bins.columns = ["Planktons", "Clownfishes", "Lionfisshes",
                       "Swordfishes", "Sharks", "Whales"]

table = [['Name', 'Estimated Balance'],
         ['Planktons', '0 to 1 Bitcoin'],
         ['Clowfishes', '1 to 10 Bitcoins'],
         ['Lionfishes', '10 to 100 Bitcoins'],
         ['Swordfishes', '100 to 1000 Bitcoins'],
         ['Sharks', '1000 to 10000 Bitcoins'],
         ['Whales', 'More than 10000 Bitcoins']]

df_table = pd.DataFrame(table)
df_table.columns = df_table.iloc[0]
df_table = df_table[1:]

df_val_per_month = pd.read_csv('change_bins_values_per_month.csv')
df_val_per_month.fillna(0, inplace=True)
df_val_per_month.loc[:,"_0_to_1":"More_10000"] = df_val_per_month.loc[:,"_0_to_1":"More_10000"].div(df_val_per_month.sum(axis=1), axis=0) * 100
df_val_per_month.columns = ["Month", "Planktons", "Clownfishes",
                            "Lionfishes", "Swordfishes", "Sharks", "Whales"]
df_val_per_month = df_val_per_month.sort_values(by='Month')
df_val_per_month.Month = pd.to_datetime(df_val_per_month.Month)
df_val_per_month = df_val_per_month.set_index(['Month'])

df_ct_per_month = pd.read_csv('change_count_bins_per_month.csv')
df_ct_per_month.fillna(0, inplace=True)
df_ct_per_month.loc[:,"_0_to_1":"More_10000"] = df_ct_per_month.loc[:,"_0_to_1":"More_10000"].div(df_ct_per_month.sum(axis=1), axis=0) * 100
df_ct_per_month.columns = ["Month", "Planktons", "Clownfishes",
                            "Lionfishes", "Swordfishes", "Sharks", "Whales"]
df_ct_per_month = df_ct_per_month.sort_values(by='Month')
df_ct_per_month.Month = pd.to_datetime(df_ct_per_month.Month)
df_ct_per_month = df_ct_per_month.set_index(['Month'])

epoch = datetime.datetime.utcfromtimestamp(0)


def unix_time_millis(dt):
    return (dt - epoch).total_seconds()

def timestamp_millis(unix_ts):
    ts = datetime.datetime.utcfromtimestamp(unix_ts).strftime('%Y-%m-%d')
    return pd.to_datetime(ts)


def build_treemap(date, x, y, width, height):

    shapes = []
    annotations = []
    counter = 0
    month = timestamp_millis(date)
    values = df_val_per_month.loc[month]
    cValues = [x + 0.0000001 for x in values]

    normed = squarify.normalize_sizes(cValues, width, height)
    print(normed)
    rects = squarify.squarify(normed, x, y, width, height)

    for r in rects:
        shapes.append(
            dict(
                type='rect',
                x0=r['x'],
                y0=r['y'],
                x1=r['x']+r['dx'],
                y1=r['y']+r['dy'],
                line={'width':2,
                      'color':'#fff'},
                fillcolor=cList[counter]
            )
        )

        counter = counter + 1
        if counter >= len(cList):
            counter = 0

    figure = {
        'data': [go.Scatter(
            x=[r['x']+(r['dx']/2) for r in rects],
            y=[r['y']+(r['dy']/2) for r in rects],
            text=[v + '\n' + '{:.2f}'.format(values.get(v)) + '%' for v in values.keys()],
            mode='text',
            hoverinfo='text',
            )
        ],

        'layout': go.Layout(
            height=700,
            width=700,
            xaxis={'showgrid': False,
                   'zeroline': False,
                   'showticklabels': False,
                   'ticks':''},
            yaxis={'showgrid': False,
                   'zeroline': False,
                   'showticklabels': False,
                   'ticks':''},
            shapes=shapes,

            hovermode='closest',
            hoverdistance=200,
        )
    }

    return figure

app.layout = html.Div([

html.Div([
    dcc.Markdown('''
    #### Bitcoin Booms and Busts: why decentralized?

    Bitcoins where created under the premise of not being centralized, therefore not controlled
    by any governments or manipulation. However, we hear about early adopters that accumulated
    large amount of bitcoins in it's early days. Are those users capable of manipulating the
    market selling their coins at once? [Were Bitcoin's early days fair?] (https://blog.picks.co/bitcoins-distribution-was-fair-e2ef7bbbc892)

    To answer that question we started with the data on the blockchain since it's first release,
    in January 9th, 2009. Even though all the data could already be accessed using a custom
    programming language, Google made the whole dataset more palatable when published it on it's
    online big data tool [Google BigQuery] (https://cloud.google.com/blog/products/gcp/bitcoin-in-bigquery-blockchain-analytics-on-public-data).

    But don't think this easy access to the data makes the transactions less private.
    To be able to track the balance of an user we need some knowledge of how the blockchain
    works, some non-trivial computer power and all addresses an user holds. For an idea,
    some users holds more than 100 address as a way to difficult hackers tracking their
    account balance, as we can see on the barchart on side.

    This way, estimations of user [balances and count] (https://medium.com/@BambouClub/are-you-in-the-bitcoin-1-a-new-model-of-the-distribution-of-bitcoin-wealth-6adb0d4a6a95) are available today, but none can
    be exact. Here we will use instant balances that are generated every time a transaction
    is made as indicators of how wealth in Bitcoin is distributed.
    '''),
    ], style= {'width': '50%', 'display': 'inline-block'}),

html.Div([
    html.Img(id='image', src='/Users/marceloqueiroz/Documents/Berkeley/Term3/w209/code/FinalProject/w209-cryptoanalysis/centralization_analysis/drawing.png'),
], style= {'width': '33%', 'display': 'inline-block'}),

html.Div([
    dash_table.DataTable(
        id = 'Table',
        columns = [{'id': c, 'name': c} for c in df_table.columns],
        data = df_table.to_dict('rows'),
        style_cell = {
            'whiteSpace': 'no-wrap',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'maxWidth': '0',
            'minWidth': '0',
            'width': '70',
        })], style= {'width': '33%', 'display': 'inline-block'}),

html.Div([
    dcc.Graph(
        id='vpm_treemap',
        figure=build_treemap(unix_time_millis(df_val_per_month.index[-1]), tm_x, tm_y, tm_width, tm_height),
        config={
            'displayModeBar': False
        }
    )
], style= {'width': '49%', 'display': 'inline-block'}),

html.Div([
    dcc.Slider(
        id='date_slider',
        min=unix_time_millis(df_ct_per_month.index.min()),
        max=unix_time_millis(df_ct_per_month.index.max()),
        value=unix_time_millis(df_ct_per_month.index.max()),
        marks={int(unix_time_millis(d)): {'label': d.strftime('%B %Y'),
                                          'style': {  'transform': 'rotate(-45deg) translate(-45px, -10px)',
                                                    'text-align': 'right',
                                                    'white-space': 'nowrap'}} for d in df_ct_per_month.index[0:len(df_ct_per_month):5]},
        included=True,
        updatemode='mouseup'
    )
], style= {'width': '100%', 'height': '100px', 'display': 'inline-block'}),

html.Div([
        dcc.Graph(
            id='cpm_treemap',
            figure=build_treemap(unix_time_millis(df_ct_per_month.index[-1]), tm_x, tm_y, tm_width, tm_height),
            config={
                'displayModeBar': False
            }
        )
], style= {'width': '49%', 'display': 'inline-block'}),



])

@app.callback(
     dash.dependencies.Output('vpm_treemap', 'figure'),
     [dash.dependencies.Input('date_slider', 'value')])
def update_vpm_treemap(date):
    pos = bisect_left(unix_time_millis(df_val_per_month.index), date)
    if pos == 0:
        return build_treemap(unix_time_millis(df_val_per_month.index[0]),
                             tm_x, tm_y, tm_width, tm_height)
    if pos == len(df_val_per_month.index):
        return build_treemap(unix_time_millis(df_val_per_month.index[-1]),
                             tm_x, tm_y, tm_width, tm_height)
    before = unix_time_millis(df_val_per_month.index[pos - 1])
    after = unix_time_millis(df_val_per_month.index[pos])
    if after - date < date - before:
        return build_treemap(after, tm_x, tm_y, tm_width, tm_height)
    else:
        return build_treemap(before, tm_x, tm_y, tm_width, tm_height)


@app.callback(
     dash.dependencies.Output('cpm_treemap', 'figure'),
     [dash.dependencies.Input('date_slider', 'value')])
def update_vpm_treemap(date):
    cDate = timestamp_millis(date)
    pos = bisect_left(df_val_per_month.index, cDate)
    if pos == 0:
        return build_treemap(df_val_per_month.index[0],
                             tm_x, tm_y, tm_width, tm_height)
    if pos == len(df_val_per_month.index):
        return build_treemap(df_val_per_month.index[-1],
                             tm_x, tm_y, tm_width, tm_height)
    before = df_val_per_month.index[pos - 1]
    after = df_val_per_month.index[pos]
    if after - cDate < cDate - before:
        return build_treemap(unix_time_millis(after), tm_x, tm_y, tm_width, tm_height)
    else:
        return build_treemap(unix_time_millis(before), tm_x, tm_y, tm_width, tm_height)

if __name__ == '__main__':
    app.run_server(debug=True)
