import dash
import sqlite3
from dash import dcc
from dash import html
import pandas as pd
import pandas_datareader.data as web
from dash import dash_table
import plotly.graph_objects as go
from datetime import datetime as dt
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(style={
    'background': 'lightgoldenrodyellow'}, children=[
    html.Div(
        html.Div(style={'textAlign': 'center', 'margin': '0 auto', 'margin-top': 20}, children=[
        html.A("Contact Info", href='https://www.ufcmachinelearning.com/contact', target="_blank")])
    ),
    html.Div(children=[
        html.Div(style={'textAlign': 'center', 'margin': '0 auto', 'margin-top': 20}, children=[
            dcc.DatePickerRange(
                id='my-date-picker-range',
                min_date_allowed=dt(1970, 1, 1),
                max_date_allowed=dt.now(),
                initial_visible_month=dt.now(),
                end_date=dt.now()
            ),
            dcc.Input(style={'margin-left': 20, 'margin-right': 20}, id='input', value='', type='text'),
            html.Div(id='output-container-date-picker-range'),
            html.Div(id='output-graph'),
        ], className="six columns"),
        html.Div(style={'textAlign': 'center', 'margin': '0 auto', 'margin-top': 20}, children=[
                dcc.Tabs(id="tabs-example", value='Twitter Sentiment Search', children=[
                dcc.Tab([
                    '''
                Twitter sentiment of topic:
                    ''',
                    dcc.Input(style={'margin-top': 20}, id='input1', value='google', type='text'),
                    dcc.Graph(id='output-graph2'),
                    dcc.Interval(
                        id='interval-component',
                        interval=1 * 1000,
                        n_intervals=0
                    ),
                ], label='Twitter Sentiment Search - Click Me'),
            ], colors={
                "border": "goldenrod",
                "primary": "gold",
                "background": "Metallic gold"
            }),
        ], className="six columns"),
    ], className="row"),
    html.Div(className='row', children=[html.Div(id="tweet-table", className='col-12-lg'),
                                        dcc.Interval(
                                            id='table-update',
                                            interval=12 * 1000,
                                            n_intervals=0
                                        ),
                                        ])
])


@app.callback(
    dash.dependencies.Output('output-container-date-picker-range', 'children'),
    [dash.dependencies.Input('my-date-picker-range', 'start_date'),
     dash.dependencies.Input('my-date-picker-range', 'end_date')])
def update_output(start__date, end__date):
    global selected_start_date, selected_end_date
    try:
        string_prefix = 'You have selected: '
        if start__date is not None:
            selected_start_date = dt.strptime(start__date, '%Y-%m-%d')
            start_date_string = selected_start_date.strftime('%B %d, %Y')
            string_prefix = string_prefix + 'Start Date: ' + start_date_string + ' | '
        if end__date is not None:
            selected_end_date = dt.strptime(end__date, '%Y-%m-%d')
            end_date_string = selected_end_date.strftime('%B %d, %Y')
            string_prefix = string_prefix + 'End Date: ' + end_date_string
        if len(string_prefix) == len('You have selected: '):
            return 'Select a date to see it displayed here'
        else:
            return string_prefix
    except:
        pass


@app.callback(
    Output(component_id='output-graph', component_property='children'),
    [Input(component_id='input', component_property='value')],
)
def update_value(input_data):
    try:
        if input_data == "":
            start = '1/1/2019'
            end = dt.now()
            df = web.DataReader("GOOGL", 'yahoo', start, end)
            df.reset_index(inplace=True)
            df.set_index("Date", inplace=True)
            return dcc.Graph(
                id='chart1',
                figure={
                    'data': [
                        {'x': df.index, 'y': df.Close, 'type': 'line', 'name': input_data},
                    ],
                    'layout': {
                        'title': 'Google',
                        'paper_bgcolor': 'rgba(0,0,0,0)',
                        'plot_bgcolor': 'rgba(0,0,0,0)'
                    }
                }
            )
        elif input_data == input_data:
            start = '1/1/2019'
            end = dt.now()
            df = web.DataReader(input_data, 'yahoo', start, end)
            df.reset_index(inplace=True)
            df.set_index("Date", inplace=True)
            return dcc.Graph(
                id='chart1',
                figure={
                    'data': [
                        {'x': df.index, 'y': df.Close, 'type': 'line', 'name': input_data},
                    ],
                    'layout': {
                        'title': input_data,
                        'paper_bgcolor': 'rgba(0,0,0,0)',
                        'plot_bgcolor': 'rgba(0,0,0,0)'
                    }
                }
            )
        else:
            start = selected_start_date
            end = selected_end_date
            df = web.DataReader(input_data, 'yahoo', start, end)
            df.reset_index(inplace=True)
            df.set_index("Date", inplace=True)
            return dcc.Graph(
                id='chart1',
                figure={
                    'data': [
                        {'x': df.index, 'y': df.Close, 'type': 'line', 'name': input_data},
                    ],
                    'layout': {
                        'title': input_data,
                        'paper_bgcolor': 'rgba(0,0,0,0)',
                        'plot_bgcolor': 'rgba(0,0,0,0)'
                    }
                }
            )
    except:
        pass


@app.callback(
    Output(component_id='output-graph2', component_property='figure'),
    [Input(component_id='input1', component_property='value'),
     Input('interval-component', 'n_intervals'),
     Input('tabs-example', 'value')]
)
def update_value2(word, n, tab):
    conn = sqlite3.connect("twitter.db")
    df = pd.read_sql_query("""SELECT * from sentiment""", conn)
    try:
        if word == "":
            df_filtered = df[df['tweet'].str.lower().str.contains(word, na=False)]
            len_items = f"{word.upper()} Data obtained from {len(df_filtered['tweet'])} tweets"
            positive_average = round(df_filtered['positive'].mean(), 2)
            negative_average = round(df_filtered['negative'].mean(), 2)
            neutral_average = round(df_filtered['neutral'].mean(), 2)
            labels = ['Positive_Score', 'Negative_Score', 'Neutral_Score']
            values = [round((positive_average * (len(df_filtered['tweet'].iloc[:]))), 0),
                      round((negative_average * (len(df_filtered['tweet'].iloc[:]))), 0)]
            colors = ['ForestGreen', 'red']
            fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
            fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20,
                              marker=dict(colors=colors, line=dict(color='#000000', width=2)))
            fig.update_layout(
                title_text=len_items,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )
            return fig
        elif word is not "":
            df_filtered = df[df['tweet'].str.lower().str.contains(word, na=False)]
            positive_average = round(df_filtered['positive'].iloc[-500:].mean(), 2)
            negative_average = round(df_filtered['negative'].iloc[-500:].mean(), 2)
            neutral_average = round(df_filtered['neutral'].iloc[-500:].mean(), 2)
            len_items = f"{word.upper()} Data obtained from {len(df_filtered['tweet'].iloc[-500:])} tweets"
            labels = ['Positive_Score', 'Negative_Score', 'Neutral_Score']
            values = [round((positive_average * (len(df_filtered['tweet'].iloc[:]))), 0),
                      round((negative_average * (len(df_filtered['tweet'].iloc[:]))), 0)]
            colors = ['ForestGreen', 'red']
            fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
            fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20,
                              marker=dict(colors=colors, line=dict(color='#000000', width=2)))
            fig.update_layout(
                title_text=len_items,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )
            return fig
    except:
        pass


@app.callback(Output(component_id='tweet-table', component_property='children'),
              [Input(component_id='input1', component_property='value'),
               Input('table-update', 'n_intervals')])
def tweet_update(term, lol):
    conn = sqlite3.connect("twitter.db")
    df = pd.read_sql_query("""SELECT * from sentiment""", conn)
    try:
        if term == "":
            df = pd.read_sql_query("""SELECT * from sentiment ORDER BY unix DESC LIMIT 14""", conn)
            df = dash_table.DataTable(
                id='table',
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
                style_cell={'textAlign': 'left'},
                style_data_conditional=[
                    {
                        'if': {
                            'filter_query': '{compound} > 0'

                        },
                        'backgroundColor': 'green',
                        'color': 'white'
                    },
                    {
                        'if': {
                            'filter_query': '{compound} < 0'

                        },
                        'backgroundColor': 'red',
                        'color': 'white'
                    }
                ]
            )
        else:
            df = pd.read_sql_query("""SELECT * from sentiment WHERE tweet LIKE ? ORDER BY unix DESC LIMIT 14""", conn,
                                   params=('%' + term + '%',))
            df = dash_table.DataTable(
                id='table',
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
                style_cell={'textAlign': 'left'},
                style_data_conditional=[
                    {
                        'if': {
                            'filter_query': '{compound} > 0'

                        },
                        'backgroundColor': 'green',
                        'color': 'white'
                    },
                    {
                        'if': {
                            'filter_query': '{compound} < 0'

                        },
                        'backgroundColor': 'red',
                        'color': 'white'

                    }
                ]
            ),
        return df
    except:
        pass


# @app.callback(Output(component_id='stock_stats', component_property='children'),
#               [Input(component_id='input', component_property='value')])
# def top_5_links(input_data):
#     try:
#         if input_data == "":
#             url = f"https://finance.yahoo.com/quote/f?p=f"
#             table = pd.read_html(url)
#             stock_df1 = table[0]
#             stock_df2 = table[1]
#             stock_df2 = stock_df2.rename(columns={0: 2, 1: 3})
#             stock_df = stock_df1.join(stock_df2, how="outer")
#             stock_df = stock_df.rename(columns={0: "Stock Details", 1: "Value", 2: "Stock Details ", 3: "Value "})
#             table1 = dbc.Table.from_dataframe(stock_df, striped=True, bordered=True, hover=True)
#             return table1
#         else:
#             url = f"https://finance.yahoo.com/quote/{input_data}?p={input_data}"
#             table = pd.read_html(url)
#             stock_df1 = table[0]
#             stock_df2 = table[1]
#             stock_df2 = stock_df2.rename(columns={0: 2, 1: 3})
#             stock_df = stock_df1.join(stock_df2, how="outer")
#             stock_df = stock_df.rename(columns={0: "Stock Details", 1: "Value", 2: "Stock Details ", 3: "Value "})
#             table1 = dbc.Table.from_dataframe(stock_df, striped=True, bordered=True, hover=True)
#             return table1
#     except:
#         pass


# @app.callback(Output(component_id='top_5_stock_links', component_property='children'),
#               [Input(component_id='input', component_property='value')])
# def top_5_links(input_data):
#     try:
#         if input_data == "":
#             global final_text
#             browser = webdriver.Chrome()
#             url = f"https://www.google.com/finance?q=f"
#             browser.get(url)
#             html_source = browser.page_source
#             browser.quit()
#             soup = bs.BeautifulSoup(html_source, "lxml")
#             links = soup.findAll('div', attrs={'class': 'dbsr'})
#             links_titles = soup.findAll('div', attrs={'class': 'nDgy9d', 'style': '-webkit-line-clamp:2'})
#             top_5 = []
#             link_title = []
#             for a in links:
#                 top_5.append(a.find('a')['href'])
#             for i in links_titles:
#                 index = links_titles.index(i)
#                 text = str(links_titles[index]).replace('<div class="nDgy9d" style="-webkit-line-clamp:2">', "")
#                 text = text.replace('</div>', "")
#                 text = text.replace(str('<\nand>'), "and")
#                 final_text = link_title.append(text)
#             return html.Div([html.A(link_title[0], href=f'{top_5[0]}', target="_blank",
#                                     style={'color': '#3F69AA', 'font-size': 21}),
#                              html.Br(),
#                              html.Br(),
#                              html.A(link_title[1], href=f'{top_5[1]}', target="_blank",
#                                     style={'color': '#3F69AA', 'font-size': 21}),
#                              html.Br(),
#                              html.Br(),
#                              html.A(link_title[2], href=f'{top_5[2]}', target="_blank",
#                                     style={'color': '#3F69AA', 'font-size': 21}),
#                              html.Br(),
#                              html.Br(),
#                              html.A(link_title[3], href=f'{top_5[3]}', target="_blank",
#                                     style={'color': '#3F69AA', 'font-size': 21}),
#                              html.Br(),
#                              html.Br(),
#                              html.A(link_title[4], href=f'{top_5[4]}', target="_blank",
#                                     style={'color': '#3F69AA', 'font-size': 21})])
#         elif input_data != "":
#             browser = webdriver.Chrome()
#             url = f"https://www.google.com/finance?q={input_data}"
#             browser.get(url)
#             html_source = browser.page_source
#             browser.quit()
#             soup = bs.BeautifulSoup(html_source, "lxml")
#             links = soup.findAll('div', attrs={'class': 'dbsr'})
#             links_titles = soup.findAll('div', attrs={'class': 'nDgy9d', 'style': '-webkit-line-clamp:2'})
#             top_5 = []
#             link_title = []
#
#             for a in links:
#                 top_5.append(a.find('a')['href'])
#             for i in links_titles:
#                 index = links_titles.index(i)
#                 text = str(links_titles[index]).replace('<div class="nDgy9d" style="-webkit-line-clamp:2">', "")
#                 text = text.replace('</div>', "")
#                 text = text.replace(str('<\nand>'), "and")
#                 final_text = link_title.append(text)
#             return html.Div([html.A(link_title[0], href=f'{top_5[0]}', target="_blank"),
#                              html.Br(),
#                              html.Br(),
#                              html.A(link_title[1], href=f'{top_5[1]}', target="_blank"),
#                              html.Br(),
#                              html.Br(),
#                              html.A(link_title[2], href=f'{top_5[2]}', target="_blank"),
#                              html.Br(),
#                              html.Br(),
#                              html.A(link_title[3], href=f'{top_5[3]}', target="_blank"),
#                              html.Br(),
#                              html.Br(),
#                              html.A(link_title[4], href=f'{top_5[4]}', target="_blank")])
#     except:
#         pass

if __name__ == '__main__':
    app.run_server(debug=True)
