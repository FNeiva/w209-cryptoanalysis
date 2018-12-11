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
import grasia_dash_components as gdc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, static_folder='static')
#app = dash.Dash(__name__)

app.index_string = '''
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
	{%metas%}
	<title>{%title%}</title>
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css?family=Roboto:100,100i,300,300i,400,400i,700,700i%7CMaitree:200,300,400,600,700&subset=latin-ext" rel="stylesheet"/>
    <!-- CSS Colors -->
    <link rel="stylesheet" type='text/css' media='all' href="static/webslides-latest/static/css/webslides.css"/>
    <!-- Optional - CSS SVG Icons (Font Awesome) -->
    <link rel="stylesheet" type='text/css' media='all' href="static/webslides-latest/static/css/svg-icons.css"/>
	{%favicon%}
	{%css%}
  <body>

	{%app_entry%}

    <script src="/static/webslides-latest/static/js/webslides.js"></script>

    <!-- OPTIONAL - svg-icons.js (fontastic.me - Font Awesome as svg icons) -->
    <script defer src="/static/webslides-latest/static/js/svg-icons.js"></script>
	<footer>
		{%config%}
		{%scripts%}
	</footer>
  </body>
 </html>
'''

slides = []
slide1 = html.Section([html.H1('Why SVG Is the Future of Web Graphics?')],className='bg-gradient-r aligncenter')
slide2 = html.Section(html.Div([
				html.Div([
					html.H2('What is SVG?'),
					html.P('Scalable Vector Graphics',className='text-subtitle'),
					html.Hr(),
					html.P('SVG is an XML-based vector graphic format used to display a wide range of graphics on the Web.',className='text-intro'),
					html.P('SVG documents are just plain text files and can be created and edited in every text editor.',className='text-intro'),
				],className='content-left'),
				html.Div([
					html.Img(src='traffic-lights.png')
				],className='content-right')
			],className='wrap')
		)
slides.append(slide1)
slides.append(slide2)
app.layout = html.Div([html.Article(slides,id="webslides"),
					   gdc.Import(src="/static/renderWebSlides.js")])

if __name__ == '__main__':
    app.run_server(debug=False)
