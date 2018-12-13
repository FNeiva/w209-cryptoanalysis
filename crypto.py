import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.tools as tools
from dash.dependencies import Input, Output, State
from dateutil.parser import parse
import squarify
import math
from datetime import datetime
from bisect import bisect_left
import grasia_dash_components as gdc

####################################################
### 			DASH SETUP CODE					 ###
####################################################

# Setup Dash's default CSS stylesheet
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Setup the Dash application
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets, static_folder='static')
app = dash.Dash(__name__, static_folder='static')


####################################################
### 		DESCENTRALIZED VIZ CODE				 ###
####################################################

tm_width = 100
tm_height = 100
tm_x = 0
tm_y = 0

# color pallette for the viz
cList = ['lightcyan', 'lightblue', 'deepskyblue', 'dodgerblue', 'steelblue',
         'midnightblue']

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

epoch = datetime.utcfromtimestamp(0)


def unix_time_millis(dt):
    return (dt - epoch).total_seconds()

def timestamp_millis(unix_ts):
    ts = datetime.utcfromtimestamp(unix_ts).strftime('%Y-%m-%d')
    return pd.to_datetime(ts)


def build_treemap(date, dataset, x, y, width, height, title):

    shapes = []
    counter = 0
    annotations = []

    month = timestamp_millis(date)

    if dataset == 'values':
        values = df_val_per_month.loc[month]
    else:
        values = df_ct_per_month.loc[month]

    cValues = [x + 0.0000001 for x in values]
    normed = squarify.normalize_sizes(cValues, width, height)
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
            ),
        )
        annotations.append(
            dict(
                x = r['x']+(r['dx']/2),
                y = r['y']+(r['dy']/2),
                text = '',
                showarrow = False,

            )
        ),


        counter = counter + 1
        if counter >= len(cList):
            counter = 0

    figure = {
        'data': [go.Scatter(
            x=[r['x']+(r['dx']/2) for r in rects],
            y=[r['y']+(r['dy']/2) for r in rects],
            text=[v + '\n' + '{:.2f}'.format(values.get(v)) + '%' for v in values.keys()],
            mode='none',
            hoverinfo='text',
            )
        ],

        'layout': go.Layout(
            #height=440,
            #width=420,
            title=title,
            xaxis={'showgrid': False,
                   'zeroline': False,
                   'showticklabels': False,
                   'ticks':''},
            yaxis={'showgrid': False,
                   'zeroline': False,
                   'showticklabels': False,
                   'ticks':''},
            shapes=shapes,
            paper_bgcolor='#f7f9fb',
            plot_bgcolor='#f7f9fb',
            margin={'l': 10, 'b': 10, 't': 30, 'r': 10},
            hovermode='closest',
            hoverdistance=200,
        )
    }

    return figure

decentralizedviz = html.Div(className='wrap',children=[
                        html.H2('Are Bitcoins Decentralized?'),
                        html.P('By dragging the slider, we can see how Bitcoin is evolving towards more centralization.',className='text-intro'),
                        html.Div(className='grid',children=[
                            html.Div(className='column',children=[
                                dcc.Graph(
                                    id='cpm_treemap',
                                    figure=build_treemap(unix_time_millis(df_ct_per_month.index[-1]),
                                                         'count', tm_x, tm_y, tm_width, tm_height,'% of Total Changes'),
                                    config={
                                        'displayModeBar': False
                                    }
                                )
                            ]),
                            html.Div(className='column',children=[
                                dcc.Graph(
                                    id='vpm_treemap',
                                    figure=build_treemap(unix_time_millis(df_val_per_month.index[-1]),
                                                         'values', tm_x, tm_y, tm_width, tm_height, '% of Total Volume'),
                                    config={
                                        'displayModeBar': False
                                    }
                                )
                            ])
                        ]),
                        html.Div(dcc.Slider(
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
                        ))
                    ])


####################################################
### 			STORE VALUE VIZ CODE			 ###
####################################################

df_storevalue = pd.read_csv('crypto10-markets-am.csv')

storevalueviz = html.Div(children = [
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
            x = df_storevalue[df_storevalue['name'] == i].date,
            y = df_storevalue[df_storevalue['name'] == i]['change%'],
            name=i
        )
        for i in df_storevalue.name.unique()],


                'layout': go.Layout(
				paper_bgcolor='#f7f9fb',
		    	plot_bgcolor='#f7f9fb',
                xaxis={'type': 'date', 'title': 'Date'},
                yaxis={'type': 'linear', 'title': '% Change in Day', 'tickformat': ',.000001%'},
                margin={'l': 100, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest')

        }
    )
])

####################################################
### 		FAST AND CHEAP VIZ CODE				 ###
####################################################

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
        #width=width,
        #height=height,
		autosize=True,
		margin=go.layout.Margin(
	        l=50,
	        r=10,
	        b=40,
	        t=20,
	        pad=4
    	),
        hovermode='closest',
        xaxis=dict(
            domain=[0, 0.45],
            anchor='y1',
            title='Date'
        ),
        yaxis=dict(
            domain=[0, 0.45],
            anchor='x1',
            title='Avg. Transaction Fees (USD)'
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
            title='Avg. Block Times (min)'
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
                  layer= "below")],
		paper_bgcolor='#f7f9fb',
    	plot_bgcolor='#f7f9fb'
    )

    return go.Figure(data=traces,layout=layout)

initial_figure = build_plots()

fastcheapviz = html.Div(className='wrap',children=[
                        html.H2('Fast and Cheap Transactions'),
                        html.P('''On the left side, you can visualize time series on historical data for block times (the amount of time it takes for a
                        transaction to show up on a block, thus being confirmed) and the fee charged for that transaction. On the right side, the
                        positioning of each cryptocurrency is relative to it\'s historical performance in both time and cost.'''),
                        html.Div(className='aligncenter',children=[
                            html.Ul(className='flexblock',children=[
            					html.Li([
            						html.H6('Start Date'),
            						dcc.Input(
            		                    id='start_date_input',
            							type='date',
            		                    min=min_date,
            		                    max=max_date,
            							value=min_date
            	                	)
            					],style={'padding-top':'1rem','padding-bottom':'1rem'}),
            					html.Li([
            						html.H6('End Date'),
            						dcc.Input(
            				            id='end_date_input',
            							type='date',
            				            min=min_date,
            				            max=max_date,
            							value=max_date
            			        	)
            					],style={'padding-top':'1rem','padding-bottom':'1rem'})]
            				),
                            dcc.Graph(
                                id='fastandcheap',
                                figure=initial_figure,
                                config={
                                    'displayModeBar': False
                                }
                            )
        			  ])
                ])

####################################################
### 			SLIDES NAVIGATION BAR			 ###
####################################################

# Defines the Navigation Bar to placed in specific slides
navbar = html.Header([
			html.Nav(role='navigation', className='navbar',children=[
				html.Ul([
						html.Li([html.A('Home',href='#slide=1')]),
						html.Li([html.A('Instructions',href='#slide=2')]),
						html.Li([html.A('Story',href='#slide=3')]),
						html.Li([html.A('Decentralization',href='#slide=5')]),
                        html.Li([html.A('Store Value',href='#slide=7')]),
						html.Li([html.A('Fast and Cheap',href='#slide=9')])
				],style={'margin':0})
			])
		])

####################################################
### 				SLIDES CODE					 ###
####################################################

# This sets up the code for the slides

slides = []

## SLIDE 1: Title Slide`
slide1 = html.Section([
				html.Img(src='/static/bitcoin_logo.svg',width='10%',height='10%',className='aligncenter'),
				html.H1(html.Strong('Bitcoin Booms and Busts')),
				html.Hr(),
				html.H5('University of California, Berkeley'),
				html.H5('Master of Information and Data Science'),
				html.H5('W209 - Data Visualization'),
				html.Hr(),
				html.H6('Arnobio Morelix'),
				html.H6('Felipe Campos'),
				html.H6('Marcelo Queiroz')],
		  className='bg-apple aligncenter')

## SLIDE 2: Instructions Slide
slide2 = html.Section([navbar,
				html.Div(className='wrap',children=[
					html.H2('Instructions'),
					html.P('How to use and navigate this website',className='text-subtitle'),
					html.Hr(),
					html.Div(className='grid',children=[
						html.Div(className='column',children=[
							html.H3('Story Mode'),
							html.P('To view the story, just keep scrolling! You can return to the beginning of the story by using the navigation bar above.')
						]),
						html.Div(className='column',children=[
							html.H3('Visualizations'),
							html.P('You can jump directly to the specific visualizations you are insterested in at any time using the navigation bar.')
						]),
						html.Div(className='column',children=[
							html.H3('Interact!'),
							html.P('You can interact with all visualizations. Drag on them to zoom in, double-click to zoom-out. Hover over points for more details. Click on items in the legend to make them disappear, or double-click to single them out!')
						])
					])
				])
			])

## SLIDE3: Story Introduction
slide3 = html.Section([navbar,
                        html.Div(className='wrap',children=[
                            html.Div(className='card-20',children=[
                                html.Div(className='flex-content',children=[
                                    html.H3('Introduction'),
                                    html.P(['Bitcoin is a ',html.Strong('cryptocurrency'),'''
                                    , which is a form of electronic cash. It''s main differentiator is that is decentralized, meaning it does not
                                    have a bank or any other kind of administrator behind it, with transactions occuring directly between users
                                    in a peer-to-peer fashion and without intermediaries. It relies on miners to process the transactions, who
                                    mine the distributed ledger called blockchain in exchange for bitcoins.

                                    Bitcoin''s main premises, which we'll analyze here, are:
                                    ''']),
                                    html.Ul(className='flexblock specs',children=[
                                        html.Li(html.Div([
                                            html.Img(src='/static/decentralized.svg'),
                                            html.H2('Decentralized'),
                                            'Lorem ipsum'
                                        ])),
                                        html.Li(html.Div([
                                            html.Img(src='/static/storevalue.svg'),
                                            html.H2('Store of Value'),
                                            'Lorem ipsum'
                                        ])),
                                        html.Li(html.Div([
                                            html.Img(src='/static/transactions.svg'),
                                            html.H2('Fast and Cheap Transactions'),
                                            'Lorem ipsum'
                                        ]))
                                    ])
                                ]),
                                html.Div(className='flex-content',children=[
                                    html.Figure(html.Img(className='alignright size-75',src='/static/bitcoin_pile.png',alt='Bitcoin'))
                                ])
                            ])
                        ])
                    ])

## SLIDE 4: Decentralization Story
slide4 = html.Section(className='bg-light',style={'background-color':'#edf2f7'},children=[navbar,
            html.Div(className='wrap',children=[
                html.Img(className='alignleft size-50',src='/static/wallets_count.svg'),
                html.H2(html.Strong('Are Bitcoins Decentralized?')),
                html.P(['Analyzing transaction data from ',html.A('January 2009 to september 2018',href='https://cloud.google.com/blog/products/gcp/bitcoin-in-bigquery-blockchain-analytics-on-public-data'),'.',
                            html.Br(),html.Br(),
                            'Bitcoins were supposed to be centralized, therefore not controlled by governments or companies. However, the early distribution was ',
                            html.A('concentrated on a few early adopters', href='https://blog.picks.co/bitcoins-distribution-was-fair-e2ef7bbbc892/'),
                            ' and nowadays specialists suspect that trader companies have the wealthier accounts.',
                            html.Br(),html.Br(),
                            'The problem can be even worse, because most of the wealthier users hold more than one account, improving his/her privacy at the same time that undermines the coin distribution transparency. For the 22 million unique wallets, the estimative is about roughly ',
                            html.A('5 million unique users',href='https://medium.com/@BambouClub/are-you-in-the-bitcoin-1-a-new-model-of-the-distribution-of-bitcoin-wealth-6adb0d4a6a95'),'.'])
                ])
            ])

## SLIDE 5: Decentralized Visualization
slide5 = html.Section([navbar,decentralizedviz])

## SLIDE 6: Store Value Story
slide6 = html.Section(className='bg-apple',children=[navbar,
            html.Div(className='wrap',children=[
                html.Img(className='alignright size-40',src='/static/speedcost.svg'),
                html.H2(html.Strong('Fast and Cheap Transactions. Really?')),
                html.P(['One of the premises of Bitcoin is to perform transactions quickly and with small fees. But how do those work',
                        ' in cryptocurrencies?',
                        ' All transactions are stored in a transaction ledger, called ',html.Strong('blockchain'),'.',
                        ' Cryptocurrency miners mine the blockchain for transactions, and when they do so they create new blocks confirming ',
                        'those transactions. Therefore, the time to confirm a transaction is usually the cryptocurrency\'s ',html.Strong('block time'),
                        '. When the miner mines a transaction, he also takes some currency for himself, which is the ',html.Strong('transaction fee'),'.',
                        html.Br(),html.Br(),
                        'When analyzing historical Bitcoin data, we can see that it has in fact been serving fast and cheap transactions, ',
                        'at least when compared to traditional banks transfers, but not credit cards and other services such as PayPal, with ',
                        'transactions being confirmed on average in 10 minutes. Fees are much lower, though, with the average historical fee ',
                        'around only a single dollar. When compared to other cryptocurrencies, though, Bitcoin suffers, offering the most ',
                        'expensive and slowest transactions of all the major cryptocurrencies. Also, when a boom in cryptocurrencies started ',
                        'occuring in the end in 2017 fees went sky high to an average of 54 dollars, showing that the currency is also very volatile.',
                        html.Br(),html.Br(),
                        'You can explore those insights and compare cryptocurrencies\' historical behavior on this premise in our next visualization.'])
        ])
    ])

## SLIDE 7: Store value Visualization
slide7 = html.Section([navbar,storevalueviz])

## SLIDE 8: Fast and Cheap Story
slide8 = html.Section(className='bg-apple',children=[navbar,
            html.Div(className='wrap',children=[
                html.Img(className='alignright size-40',src='/static/speedcost.svg'),
                html.H2(html.Strong('Fast and Cheap Transactions. Really?')),
                html.P(['One of the premises of Bitcoin is to perform transactions quickly and with small fees. But how do those work',
                        ' in cryptocurrencies?',
                        ' All transactions are stored in a transaction ledger, called ',html.Strong('blockchain'),'.',
                        ' Cryptocurrency miners mine the blockchain for transactions, and when they do so they create new blocks confirming ',
                        'those transactions. Therefore, the time to confirm a transaction is usually the cryptocurrency\'s ',html.Strong('block time'),
                        '. When the miner mines a transaction, he also takes some currency for himself, which is the ',html.Strong('transaction fee'),'.',
                        html.Br(),html.Br(),
                        'When analyzing historical Bitcoin data, we can see that it has in fact been serving fast and cheap transactions, ',
                        'at least when compared to traditional banks transfers, but not credit cards and other services such as PayPal, with ',
                        'transactions being confirmed on average in 10 minutes. Fees are much lower, though, with the average historical fee ',
                        'around only a single dollar. When compared to other cryptocurrencies, though, Bitcoin suffers, offering the most ',
                        'expensive and slowest transactions of all the major cryptocurrencies. Also, when a boom in cryptocurrencies started ',
                        'occuring in the end in 2017 fees went sky high to an average of 54 dollars, showing that the currency is also very volatile.',
                        html.Br(),html.Br(),
                        'You can explore those insights and compare cryptocurrencies\' historical behavior on this premise in our next visualization.'])
        ])
    ])

## SLIDE 9: Fast and cheap Visualization
slide9 = html.Section([navbar,fastcheapviz])

## SLIDE 10: Story Conclusion
slide10 = html.Section(className='bg-apple',children=[navbar,
            html.Div(className='wrap',children=[
                html.Img(className='alignright size-40',src='/static/speedcost.svg'),
                html.H2(html.Strong('Fast and Cheap Transactions. Really?')),
                html.P(['One of the premises of Bitcoin is to perform transactions quickly and with small fees. But how do those work',
                        ' in cryptocurrencies?',
                        ' All transactions are stored in a transaction ledger, called ',html.Strong('blockchain'),'.',
                        ' Cryptocurrency miners mine the blockchain for transactions, and when they do so they create new blocks confirming ',
                        'those transactions. Therefore, the time to confirm a transaction is usually the cryptocurrency\'s ',html.Strong('block time'),
                        '. When the miner mines a transaction, he also takes some currency for himself, which is the ',html.Strong('transaction fee'),'.',
                        html.Br(),html.Br(),
                        'When analyzing historical Bitcoin data, we can see that it has in fact been serving fast and cheap transactions, ',
                        'at least when compared to traditional banks transfers, but not credit cards and other services such as PayPal, with ',
                        'transactions being confirmed on average in 10 minutes. Fees are much lower, though, with the average historical fee ',
                        'around only a single dollar. When compared to other cryptocurrencies, though, Bitcoin suffers, offering the most ',
                        'expensive and slowest transactions of all the major cryptocurrencies. Also, when a boom in cryptocurrencies started ',
                        'occuring in the end in 2017 fees went sky high to an average of 54 dollars, showing that the currency is also very volatile.',
                        html.Br(),html.Br(),
                        'You can explore those insights and compare cryptocurrencies\' historical behavior on this premise in our next visualization.'])
        ])
    ])

slides.append(slide1)
slides.append(slide2)
slides.append(slide3)
slides.append(slide4)
slides.append(slide5)
slides.append(slide6)
slides.append(slide7)
slides.append(slide8)
slides.append(slide9)
slides.append(slide10)

####################################################
### 				DASH LAYOUT					 ###
####################################################

# Set the Dash layout using the slides designed above
app.layout = html.Div([html.Main(role='main',children=[
					   		html.Article(slides,id="webslides",className='vertical')]),
					   gdc.Import(src="/static/renderWebSlides.js")])

####################################################
### 			VISUALIZATION CALLBACKS			 ###
####################################################

################################
##  Descentralized Callbacks  ##
################################

@app.callback(
     dash.dependencies.Output('vpm_treemap', 'figure'),
     [dash.dependencies.Input('date_slider', 'value')])
def update_vpm_treemap(date):
    pos = bisect_left(unix_time_millis(df_val_per_month.index), date)
    if pos == 0:
        return build_treemap(unix_time_millis(df_val_per_month.index[0]),
                             'values', tm_x, tm_y, tm_width, tm_height,'% of Total Volume')
    if pos == len(df_val_per_month.index):
        return build_treemap(unix_time_millis(df_val_per_month.index[-1]),
                             'values', tm_x, tm_y, tm_width, tm_height,'% of Total Volume')
    before = unix_time_millis(df_val_per_month.index[pos - 1])
    after = unix_time_millis(df_val_per_month.index[pos])
    if after - date < date - before:
        return build_treemap(after,'values', tm_x, tm_y, tm_width, tm_height,'% of Total Volume')
    else:
        return build_treemap(before,'values', tm_x, tm_y, tm_width, tm_height,'% of Total Volume')


@app.callback(
     dash.dependencies.Output('cpm_treemap', 'figure'),
     [dash.dependencies.Input('date_slider', 'value')])
def update_vpm_treemap(date):
    cDate = timestamp_millis(date)
    pos = bisect_left(df_ct_per_month.index, cDate)
    if pos == 0:
        return build_treemap(df_ct_per_month.index[0],
                             'count', tm_x, tm_y, tm_width, tm_height,'% of Total Changes')
    if pos == len(df_ct_per_month.index):
        return build_treemap(df_ct_per_month.index[-1],
                             'count', tm_x, tm_y, tm_width, tm_height,'% of Total Changes')
    before = df_ct_per_month.index[pos - 1]
    after = df_ct_per_month.index[pos]
    if after - cDate < cDate - before:
        return build_treemap(unix_time_millis(after),'count', tm_x,
                             tm_y, tm_width, tm_height,'% of Total Changes')
    else:
        return build_treemap(unix_time_millis(before),'count', tm_x,
                             tm_y, tm_width, tm_height,'% of Total Changes')


################################
## Fast and Cheap Callbacks   ##
################################

@app.callback(
    Output('fastandcheap', 'figure'),
    [Input('start_date_input', 'value'),
     Input('end_date_input', 'value')])
def display_selected_data(start_date,end_date):
	if (start_date == ''):
		start_date = min_date
	else:
		start_date = parse(start_date).date()
	if (end_date == ''):
		end_date = max_date
	else:
		end_date = parse(end_date).date()
	if ((start_date == str(min_date.date())) and (end_date == str(max_date.date()))):
		return initial_figure
	else:
		return build_plots(initial_date=start_date,end_date=end_date,zoom=True)

@app.callback(
    Output('start_date_input', 'value'),
    [Input('fastandcheap', 'relayoutData')])
def zoom_to_start_date(relayoutData):
    if (relayoutData is None):
        return min_date
    if ('xaxis.range[0]' in relayoutData):
        initial_date = parse(relayoutData['xaxis.range[0]'])
        return initial_date.date()
    else:
        return min_date

@app.callback(
    Output('end_date_input', 'value'),
    [Input('fastandcheap', 'relayoutData')])
def zoom_to_end_date(relayoutData):
    if (relayoutData is None):
        return max_date
    if ('xaxis.range[1]' in relayoutData):
        end_date = parse(relayoutData['xaxis.range[1]'])
        return end_date.date()
    else:
        return max_date


####################################################
### 			DASH INITIALIZATION				 ###
####################################################

# Fire up the Dash Server
if __name__ == '__main__':
    app.run_server(debug=True)
