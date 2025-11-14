from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dbc.Row([
        html.H1("Hallo Projektphase 1", id="h-1")
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Slider(min=1, max=100, id="slider-1")
        ], width=2),
        dbc.Col([
            dcc.Dropdown(options=[
                {"label": "Hallo", "value": "Hallo"},
                {"label": "Servus", "value": "Servus"}
            ], id="dd-1")
        ]),
        dbc.Col([
            dcc.Dropdown(options=[
                {"label": "DD2 Hallo", "value": "DD2 Hallo"},
                {"label": "DD2 Servus", "value": "DD2 Servus"}
            ], id="dd-2")
        ])
    ])
])


@app.callback(
    Output("h-1", "children"),
    Input("dd-1", "value")
) 
def change_greeting(in1):
    return f"{in1} du!"

@app.callback(
    Output("h-1", "children", allow_duplicate = True),
    Input("dd-2", "value"),
    prevent_initial_call = True
) 
def change_name(in1):
    return f"{in1} du!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
