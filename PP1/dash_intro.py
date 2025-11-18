from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import sys

df = pd.read_csv('line_test_2025-11-18_10-00-38.csv')
df_speed = df[['time', 'speed']].dropna()
print("ok")
#df_speed["time"] = pd.to_datetime(df_speed["time"])
print(df_speed)
print('ok')
df_speed["time_diff"] = df_speed["time"].diff()
df_speed["v_avg"] = (df_speed["speed"] + df_speed["speed"].shift()) / 2
df_speed["distance"] = df_speed["v_avg"] * df_speed["time_diff"]
total_distance = df_speed["distance"].sum()
total_driving_time = df_speed["time_diff"].sum()
print(total_driving_time, total_distance / 3600)
print(df_speed["time"].iloc[-1] - df_speed["time"].iloc[0])



#df_speed = df[['time', 'speed', 'time_diff']].dropna()
#df_speed = df[['time', 'speed', 'time_diff']].dropna()
print(df_speed)
#sys.exit()
df_speed.to_csv('./strecke.csv')
sys.exit()
print(df_speed['speed'].values.max())
print(df_speed['speed'].values.min())
print(df_speed['speed'].values.mean())
print(df["time_diff"])
#print(df_speed)
#df.to_csv('./strecke.csv')
sys.exit()
df_speed = df_speed.dropna()
print(df_speed)
sys.exit()
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])



app.layout = html.Div([
    dbc.inngoRow([
        html.H1("Hallo Projektphase 1", id="h-1")
    ]),
    dbc.Row([
        dbc.Col([dcc.Slider(min=1, max=100, id="slider-1")], width=2),
        dbc.Col([dcc.Dropdown(options=[
            {"label": "Hallo", "value": "Hallo"},
            {"label": "Servus", "value": "Servus"}], id="dd-1")]),
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
