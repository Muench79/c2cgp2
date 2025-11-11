import dash
from dash import dcc
from dash import html
import plotly.express as px
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# Verwendung von externen Stylesheets
app = dash.Dash(external_stylesheets=[dbc.themes.DARKLY])

df = px.data.stocks()

# Definition eines dbc Element für die spätere Verwenung im Layout
card = dbc.Card(
    [
        dbc.CardImg(src="/static/images/squirrel.png", top=True),
        dbc.CardBody(
            [
                html.H4("Eichhörnchen", className="card-title"),
                html.P(
                    "Guten Tag",
                    className="card-text",
                ),
            ]
        ),
    ],
    style={"width": "18rem"},
)

app.layout = html.Div(
    children=[
        dbc.Row([
            dbc.Col([card], width=4),
            dbc.Col([card], width=4),
            dbc.Col([card], width=4)
        ], align='center'),
        html.H2(id='titel',
                children='Aktienkurse'),
        html.Div(children='Wählen Sie eine anzuzeigende Aktie aus.'),
        dcc.Dropdown(id='dropdown',
                     options=[
                         {'label': 'Google', 'value': 'GOOG'},
                         {'label': 'Apple', 'value': 'AAPL'},
                         {'label': 'Amazon', 'value': 'AMZN'},
                     ],
                     value='GOOG'),
        dcc.Graph(id='line_plot'),
        html.Br(),
        
    ]
)


# Callback für den Plot als Ausgabe (siehe 'line_plot') und den Wert des Dropdown Menüs als Eingabe
@app.callback(Output(component_id='line_plot', component_property='figure'),
              [Input(component_id='dropdown', component_property='value')])
def graph_update(value_of_input_component):
    print(value_of_input_component)
    fig = px.line(df, x=df['date'], y=df[value_of_input_component])
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
    #app.run_server(host = '0.0.0.0', port=8080, debug=True)
