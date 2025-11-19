from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import matplotlib.pyplot as plt
import pandas as pd
import sys
import math
import plotly.express as px


# Max speed
# Min speed
# Mean speed
# Distance
# Total travel time

df = pd.read_csv('line_test_2025-11-19_07-01-54.csv')
df["time"] = pd.to_datetime(df["time"], unit="s")

df["time_s"] = (df["time"] - df["time"].iloc[0]).dt.total_seconds()
df_speed = df[["time_s", "speed"]].dropna()
df_steering_angle = df[["time_s", "steering_angle"]].dropna()
df_infrared_analog_0 = df[["time_s", "infrared_analog_0"]].dropna()
df_infrared_analog_1 = df[["time_s", "infrared_analog_1"]].dropna()
df_infrared_analog_2 = df[["time_s", "infrared_analog_2"]].dropna()
df_infrared_analog_3 = df[["time_s", "infrared_analog_3"]].dropna()
df_infrared_analog_4 = df[["time_s", "infrared_analog_4"]].dropna()

first = True
speed = 0
speed_max = -999
speed_min = 999
distance = 0
time_s = 0
time_t = 0

for row in df_speed.itertuples(index=False):
    if first:
        first = False
        speed = row.speed
        time_s = row.time_s
    else:
        time_t += row.time_s - time_s
        distance += speed * (row.time_s - time_s)
        speed = row.speed
        time_s = row.time_s
    if speed > speed_max:
        speed_max = speed
    if speed < speed_min:
        speed_min = speed
    
try:
    speed_mean = distance / time_t
except:
    pass

print(speed_max, speed_min, distance / 3600, time_t, (distance / time_t))

"""


sys.exit()








#df["delta_t"] = df["time_s"].diff().fillna(0)
#df_speed["time_delta"] = df_speed["time_s"].diff()
df_speed["time_delta"] = df_speed["time_s"].shift(-1) - df_speed["time_s"]
df_speed["distance"] = df_speed["speed"].shift(-1) * df_speed["time_delta"]

speed_max = df_speed['speed'].max()
speed_min = df_speed['speed'].min()

time_total_travel = df_speed["time_s"].iloc[-1] - df_speed["time_s"].iloc[0]
distance = df_speed["distance"].sum()

speed_mean = distance / time_total_travel
print(speed_mean,distance,time_total_travel )

print(df_speed)
print()
sys.exit()
time_total_travel = df["time_s"].iloc[-1]

speed_min = df['speed'].min()


print(time_total_travel, speed_max, speed_min, )

sys.exit()

print(df["time"].dtype)

df_speed = df[['time_ms', 'speed']]
df_speed = df_speed.dropna()
df_infrared_analog_0 = df[['time_ms', 'infrared_analog_0']]
df_infrared_analog_0 = df_infrared_analog_0.dropna()
df_infrared_analog_1 = df[['time_ms', 'infrared_analog_1']]
df_infrared_analog_1 = df_infrared_analog_1.dropna()
df_infrared_analog_2 = df[['time_ms', 'infrared_analog_2']]
df_infrared_analog_2 = df_infrared_analog_2.dropna()
df_infrared_analog_3 = df[['time_ms', 'infrared_analog_3']]
df_infrared_analog_3 = df_infrared_analog_3.dropna()
df_infrared_analog_4 = df[['time_ms', 'infrared_analog_4']]
df_infrared_analog_4 = df_infrared_analog_4.dropna()
df_steering_angle = df[['time_ms', 'steering_angle']]
df_steering_angle = df_steering_angle.dropna()
drive_time = df_speed["time_ms"].iloc[-1] - df_speed["time_ms"].iloc[0]
print(math.ceil(drive_time))
plt.figure(figsize=(15, 8))  # Diagrammgröße festle
plt.step(x=df_speed["time_ms"], y=df_speed["speed"], where="post", label="Geschwindigkeit")
plt.step(x=df_steering_angle["time_ms"], y=df_steering_angle["steering_angle"], where="post", label="Lenkwinkel")
plt.step(x=df_infrared_analog_0["time_ms"], y=df_infrared_analog_0["infrared_analog_0"], where="post", label="IR 0")
plt.step(x=df_infrared_analog_1["time_ms"], y=df_infrared_analog_1["infrared_analog_1"], where="post", label="IR 1")
plt.step(x=df_infrared_analog_2["time_ms"], y=df_infrared_analog_2["infrared_analog_2"], where="post", label="IR 2")
plt.step(x=df_infrared_analog_3["time_ms"], y=df_infrared_analog_3["infrared_analog_3"], where="post", label="IR 3")
plt.step(x=df_infrared_analog_4["time_ms"], y=df_infrared_analog_4["infrared_analog_4"], where="post", label="IR 4")
plt.xlabel("Zeit")
plt.ylabel("Geschwindigkeit")
plt.title("Treppenförmiges Diagramm")
plt.grid(True)
plt.xlabel("Zeit")
plt.ylabel("Geschwindigkeit")
plt.title("Treppenförmiges Diagramm")
plt.legend(loc="upper left", bbox_to_anchor=(1, 1)) 
plt.grid(True)
plt.xticks(ticks=range(0,math.ceil(drive_time) + 1), rotation=45)
plt.tight_layout()
plt.show()
plt.savefig("./zzz2.png")





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
d = {}
print('gggggggg', type(d))
#x = plt.step(x=df["time"], y=df["speed"], where="post")

#x = df_speed.step(x = 'time', y = 'speed')
print(df.info())
plt.savefig("./diagramm.png")
#x.savefig( "./diagramm.png")

print(df_speed)

differenz = df["time"].iloc[59] - df["time"].iloc[0]

print(differenz)
sys.exit()
"""


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.H2("Live-Fahrdaten"),
    dbc.Row([dbc.Col("Maximale Geschwindigkeit:", width=2),
             dbc.Col(id="speed_max_output", width="auto")]),
    dbc.Row([dbc.Col("Durchschnittliche Geschwindigkeit:", width=2),
             dbc.Col(id="speed_mean_output", width="auto")]),
    dbc.Row([dbc.Col("Minimale Geschwindigkeit:", width=2),
             dbc.Col(id="speed_min_output", width="auto")]),
    dbc.Row([dbc.Col("Zurückgelegte Strecke:", width=2),
             dbc.Col(id="distance_output", width="auto")]),
    dbc.Row([dbc.Col("Farhzeit:", width=2),
             dbc.Col(id="time_t_output", width="auto")]),
    dcc.Dropdown(options=[
                {"label": "Geschwindigkeit", "value": "speed"},
                {"label": "Lenkwinkel", "value": "steering_angle"},
                {"label": "IR0", "value": "infrared_analog_0"},
                {"label": "IR1", "value": "infrared_analog_1"},
                {"label": "IR2", "value": "infrared_analog_2"},
                {"label": "IR3", "value": "infrared_analog_3"},
                {"label": "IR4", "value": "infrared_analog_4"},
            ], value="speed", id="dd_1"),
    dcc.Graph(id="chart"),
    dcc.Interval(id="interval", interval=10000, n_intervals=0)  # alle 1 Sekunde
])
#px.line(df, x="Zeit", y="Geschwindigkeit", title="Geschwindigkeit über Zeit")


@app.callback(
    Output("speed_max_output", "children"),
    Input("interval", "n_intervals")
)
def update_speed_max(n):
    return f"{speed_max:.2f} km/h"

@app.callback(
    Output("speed_mean_output", "children"),
    Input("interval", "n_intervals")
)
def update_speed_mean(n):
    return f"{speed_mean:.2f} km/h"

@app.callback(
    Output("speed_min_output", "children"),
    Input("interval", "n_intervals")
)
def update_speed_min(n):
    return f"{speed_min:.2f} km/h"

@app.callback(
    Output("distance_output", "children"),
    Input("interval", "n_intervals")
)
def update_output_distance(n):
    return f"{distance:.2f} m"
@app.callback(
    Output("time_t_output", "children"),
    Input("interval", "n_intervals")
)
def update_output_time_t(n):
    return f"{time_t:.2f} s"

@app.callback(
    Output("chart", 'figure'),
    Input("dd_1", "value")
)
def update_output_time_t(n):
    print(n)
    dfx = df_speed
    if n == "infrared_analog_0":
        dfx = df_infrared_analog_0
    elif n == "infrared_analog_1":
        dfx = df_infrared_analog_1
    elif n == "infrared_analog_2":
        dfx = df_infrared_analog_2
    elif n == "infrared_analog_3":
        dfx = df_infrared_analog_3
    elif n == "infrared_analog_4":
        dfx = df_infrared_analog_4
    elif n == "steering_angle":
        dfx = df_steering_angle
    return px.line(dfx, x="time_s", y=n, line_shape="hv", title="Geschwindigkeit")
    #return plt.step(df_speed['time_s'], x="time_s", y=n)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
