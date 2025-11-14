from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import matplotlib.pyplot as plt
import pandas as pd
import sys


df = pd.read_csv('data_2025-11-14_15-05-09.csv')
df["time"] = pd.to_datetime(df["time"], unit="s")

df_speed = df[['time', 'speed']]
df_speed = df_speed.dropna()
df_distance = df[['time', 'distance']]
df_distance = df_distance.dropna()

plt.step(x=df_speed["time"], y=df_speed["speed"], where="post")
plt.step(x=df_distance["time"], y=df_distance["distance"], where="post")

plt.xlabel("Zeit")
plt.ylabel("Geschwindigkeit")
plt.title("Treppenförmiges Diagramm")
plt.grid(True)
plt.show()

#x = plt.step(x=df["time"], y=df["speed"], where="post")

#x = df_speed.step(x = 'time', y = 'speed')
print(df.info())
plt.savefig("./diagramm.png")
#x.savefig( "./diagramm.png")

print(df_speed)

differenz = df["time"].iloc[59] - df["time"].iloc[0]

print(differenz)
sys.exit()



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
