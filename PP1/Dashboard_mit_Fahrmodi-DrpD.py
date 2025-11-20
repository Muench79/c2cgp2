#pip install dash==2.15.0 dash-bootstrap-components pandas numpy plotly

import pandas as pd
from dash import Dash, html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import numpy as np
import os
from dash.exceptions import PreventUpdate
import threading
from BaseCar_ds_ir_RM import SensorCar, run_mode                                    # BaseCar Klasse SensorCar und funktion run_mode importieren für Fahrmodusvorgabe

x = SensorCar()                                                                     # Auto-Objekt definieren mit Standardwerten

def load_data():
    """Lädt die data_storage.csv und bereitet sie auf.
       Gibt einen DataFrame zurück (kann auch leer sein)."""
    if not os.path.exists("data_storage.csv") or os.path.getsize("data_storage.csv") == 0:      #Abfragen, ob data_storage.csv existiert oder ob sie leer ist
        print("⚠️ data_storage.csv fehlt oder ist leer – Dashboard bleibt unverändert.")
        return pd.DataFrame(columns=[
            "timestamp", "speed", "steering_angle", "direction", "ultrasonic", "Infrared"       #leeres Dataframe erzeugen
        ])

    df = pd.read_csv("data_storage.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    df["fahrzeit_s"] = (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds()
    return df

Dashdf = load_data()                                                                          # csv-Datei Laden aund als Dataframe abspeichern

#-----KPIs berechnen----------------------------------
max_speed=Dashdf["speed"].max()
min_speed=Dashdf["speed"].min()
avg_speed=Dashdf["speed"].mean() #Geschwindigkeit ggf.korrigieren mit über die Strecke

#Daten für Trapezmethode vorbereiten
s = Dashdf.sort_values("timestamp").reset_index(drop=True)
t = (s["timestamp"] - s["timestamp"].iloc[0]).dt.total_seconds().to_numpy()  # (Normieren auf Startzeit Beginn bei Sekunden) iloc[0] bezeichnet ersten Wert der Spalte / .dt.total_seconds() wandelt eine Timedelta-Spalte in „Sekunden seit Start“ als Zahlenformat um
v = (s["speed"] * (1000/3600.0)).to_numpy()                    #Umwandlung in m/s  (.to_numpy() wandelt Daten in numpy-Array um (ohne Spaltenname, ohne Index))

# Trapezintegration
total_dist = np.trapz(v, t)
#total_dist = np.trapezoid(v, t)                                         # Integration mit Trapezmethode
#print(total_dist, type(total_dist))
print(f"Zurückgelegte Strecke: {total_dist:.2f} m")
# Gesamtdaur errechnen
total_time = s["timestamp"].iloc[-1] - s["timestamp"].iloc[0] # -1 letzte Wert in Spalte und 1 der erste Wert in der Spalte
#print(f"maxspeed: {max_speed}; minspeed: {min_speed}; avgspeed: {avg_speed}; totaldist: {total_dist}; totaltime: {total_time}")


# Formatierung für Zeiteiheit in Sekunden
def fmt(v, unit=""):
    return f"{v:.2f}{(' ' + unit) if unit else ''}"

def fmt_time(sec):
    sec = float(sec)
    m, s = divmod(int(round(sec)), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"
time_delta = Dashdf["timestamp"].max() - Dashdf["timestamp"].min()
total_time_sec = time_delta.total_seconds()
#print (total_time_sec)
#print(fmt_time(total_time_sec))  # z.B. 00:00:20


    # ----Dash App erzeugen----
app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])

card_style = {                                              # Stil der Karten vorgeben
    "border": "1px solid #ddd",
    "borderRadius": "6px",
    "padding": "6px 8px",
    "minWidth": "80px",
    "boxShadow": "0 2px 8px rgba(0,0,0,0.06)",
    "background": "#e6f7e6"                     #Pastellgrün: #e6f7e6, hellgrau:#e6e6e6
}
#fig Plottbefehlt mit Textausschrichtungsbeschreibung Schriftform , Schrittgröße und Fedformen
fig = px.line(Dashdf,x="timestamp",y="speed",title="<b><i>Fahrgeschwindigkeit</i></b>",labels={"timestamp": "Zeit", "speed": "Speed (m/s)"})                 # Graph vordefinieren, <b>...</b> fett geschrieben; <i>…</i> --> kursiv
fig.update_layout(title={   "x": 0.5,               # Titel ausrichten  0 = links, 0.5 = Mitte, 1 = rechts
                            "xanchor": "center"},
                  title_font=dict(size=24,           # größer
                                # family="Arial",  # optional Schriftart
                                # color="black"    # optional Farbe
                                ),
                )
# Dashboard ist in einzelne Bereiche aufgeteilt (Fahrmodus, Felder , Graphen, Dropdown für Fahrmodus)
app.layout = html.Div([                                                         # zentriert       #Schriftgröße     #schriftart kursiv      Zeilenabstand oben/unten
                    html.Div([dbc.Row([html.H3("Fahrdaten – KPIs", id="h-1", style={"textAlign": "center", "fontSize": "42px", "fontStyle": "italic", "margin": "16px 0"})]),
                    html.Div([                                                                           # Division für Dropdown Fahrmodusauswahl
                        dcc.Dropdown(                                                                    # Dropdown
                            id="drpd-1",options=[  {"label": "Fahrmodus 1", "value": "1"},               # label definiert den Anzeigenamen im Dropdown
                                                    {"label": "Fahrmodus 2", "value": "2"},              # Value definiert den Wert, der übergeben wird an die Callbackfunktion
                                                    {"label": "Fahrmodus 3", "value": "3"},
                                                    {"label": "Fahrmodus 4", "value": "4"},
                                                    {"label": "Fahrmodus 5", "value": "5"},
                                                    {"label": "Fahrmodus 6", "value": "6"}, 
                                                    {"label": "Fahrmodus 7", "value": "7"},
                                                    {"label": "Fahrmodus 8", "value": "8"},  
                                                        ],
                            value=None,                                                                   #Startwert bzw defaultwert
                            placeholder="Fahrmodus auswählen",
                            clearable=False,
                            style={"width": "250px"}),                                                     #Breite definieren 
                            html.Div(id="fahrmodus_status"), 
                        ],                                                                                                    
                            style={"display": "flex",                                                        # Ausrichtungs Art flex-start Links , flex-endEnd rechts
                                   "justifyContent": "flex-start",                                           # ➜ nach links ausrichten
                                    "marginBottom": "8px"},
                        ),
                        # Ausrichtung längsausrichtung der Kacheln über dbc 6x6 Feldgröße
                        dbc.Row([
                                dbc.Col(html.Div([
                                    html.Div("Min Speed [m/s]", style={"color": "#666", "fontSize": "14px"},),
                                    html.H2(fmt(min_speed, "m/s"),id="kpi-1",style={"margin": "6px 0 0"},),], style=card_style,)),
                                dbc.Col(html.Div([
                                    html.Div("Max Speed [m/s]",style={"color": "#666", "fontSize": "14px"},),
                                    html.H2(fmt(max_speed, "m/s"),id="kpi-2",style={"margin": "6px 0 0"},),],style=card_style,)),
                                dbc.Col(html.Div([
                                    html.Div("Mean Speed [m/s]",style={"color": "#666", "fontSize": "14px"},),
                                    html.H2(fmt(avg_speed, "m/s"),id="kpi-3",style={"margin": "6px 0 0"},),],style=card_style,)),
                                dbc.Col(html.Div([
                                    html.Div("„zurückgelegte Strecke“ [m]",style={"color": "#666", "fontSize": "14px"},),
                                    html.H2(fmt(total_dist, "m"),id="kpi-4",style={"margin": "6px 0 0"},),],style=card_style,)),
                                dbc.Col(html.Div([
                                    html.Div("„gesamte Fahrzet [s]“ ",style={"color": "#666", "fontSize": "14px"},),
                                    html.H2(fmt_time(total_time_sec),id="kpi-5",style={"margin": "6px 0 0"},),],style=card_style,)),
                                ]),
                            ],
                        style={"display": "flex",               #Div als Flex Container definieren --> alle Kinder (also dbc.Row un Col) werden von Flexbox angeordnet
                                "gap": "16px",                  # Abstand zwischen den einzelnen boxen
                                "flexWrap": "wrap",             # Wenn nicht genug Platz in der Hauptrichtung ist, dürfen Elemente in die nächste Zeile/Spalte umbrechen
                                "alignItems": "stretch",        # Bestimmt die Ausrichtung quer zur Hauptrichtung, "row" → vertikal, "column" → horizontal,"stretch" → Kinder werden so weit wie möglich „aufgezogen“
                                "flexDirection": "column",      #Hauptrichtung der Anordnung der Boxen (hier Spaltenausrichtung)
                                }
                            ),
                    html.Br(),                             # etwas Abstand
                     
    
                    html.Div([
                        html.Div(                          # Dropdown oben rechts über dem Diagramm
                            dcc.Dropdown(
                                id="drpd-2",options=[  {"label": "Geschwindigkeit [m/s]", "value": "speed"},                    # label definiert den Anzeigenamen im Dropdown
                                                        {"label": "Lenkwinkel [Grad]", "value": "steering_angle"},              # Value definiert den Wert, der übergeben wird an die Callbackfunktion
                                                        {"label": "Fahrtrichtung [-]", "value": "direction"},
                                                        {"label": "Abstand z. Hinderniss [-]", "value": "ultrasonic"}, 
                                                            ],
                                value="speed",                                          #Startwert bzw defaultwert
                                clearable=False,
                                style={"width": "250px"}),                              #Breite definieren
                            style={"display": "flex",
                                   "justifyContent": "flex-end",  # ➜ nach rechts schieben
                                    "marginBottom": "8px"},
                            ),
                    dcc.Graph(id="gr-1",figure=fig),
                    dcc.Interval(id="int-1", interval=5*1000, n_intervals=0)                           # Intervall einfügen, dass alle 5sec triggert (kein sichtbarer Inhalt)
                        ])
                    ])
# Ende der Seite bzw. Formatdefinition

@app.callback(                                                                      # callback Fahrmodus
    Output("fahrmodus_status", "children"),                                          # Children muss angegeben werden damit der Output funktioniert
    Input("drpd-1", "value"),
    prevent_initial_call=True,                                                       #Nicht den ersten Wert verwenden Bsp. Überschrift als Platzhalter 
)
def start_fahrmodus(value):                 
    if value is None or value == "0":
        raise PreventUpdate                                                         # Nicht Updaten wenn Funktion aktiv ist

    fmod = int(value)

    # Thread starten, der run_mode ausführt Damit wrd verhindert das der Browser einfriert
    # Funktionion wirt in BasCar definiert def run_mode Python vergibt intern den Namen IF _name main
    t = threading.Thread(target=run_mode, args=(fmod, x), daemon=True)
    t.start()

    return f"Fahrmodus {fmod} gestartet."


@app.callback(		                                                    #Callbackfunktion Dropdown
            Output("gr-1","figure"),                                    # Figure soll geändert werden
            Output("kpi-1", "children"),                                #Box 1 mit min_speed
            Output("kpi-2", "children"),                                #Box 2 mit max_speed
            Output("kpi-3", "children"),                                #Box 3 mit avg_speed
            Output("kpi-4", "children"),                                #Box 4 mit total-dist
            Output("kpi-5", "children"),	                            #Box 5 mit total_time	
            Input("drpd-2", "value"),                                   # Wert von Callback erfragen
            Input("int-1", "n_intervals"),                              # ➜ triggert alle 5 s das Callback
            State("drpd-2", "options")                                  # zusätzlich dir Options aus Zeile 85 bis 88 übergeben                               
    )


def update_graph_kpis(sel_value, n_intervals, options):                  # mit dieser Zeile wird Wert von Dropdown an sel_value übergeben
                                                               
    Dashdf = load_data()                                            # CSV jedes Mal frisch einlesen
    if Dashdf.empty:                                                # leere Datei → nichts ändern
        raise PreventUpdate                                         #  Alles, was nach raise PreventUpdate kommt, wird NICHT mehr ausgeführt.(Dash versteht es so: „Callback ist gelaufen, aber Outputs bitte nicht anfassen)
        

    #--------------- KPIs neu berechnen------------------------------------------------
    max_speed=Dashdf["speed"].max()
    min_speed=Dashdf["speed"].min()
    avg_speed=Dashdf["speed"].mean()

    s = Dashdf.sort_values("timestamp").reset_index(drop=True)
    t = (s["timestamp"] - s["timestamp"].iloc[0]).dt.total_seconds().to_numpy()
    v = (s["speed"] * (1000 / 3600.0)).to_numpy()
    total_dist = np.trapz(v, t)

    time_delta = Dashdf["timestamp"].max() - Dashdf["timestamp"].min()
    total_time_sec = time_delta.total_seconds()



    label = sel_value                                               # Fallback wenn if Schleife nichts findet
    for opt in options:                                             # Schleife, um die Options durchzugehen opt wäre in der Matlabwelt options(i)
        if opt["value"]==sel_value:                                 # wenn opt und sel_value übereinstimmen 
            label=opt["label"]                                      # dann label aus opt rausschreiben
            break                                                   # for-Schleife abbrechen

    fig = px.line(Dashdf,x="timestamp",y=sel_value,title=f"<b><i>{label}</i></b>",labels={"timestamp": "Zeit", sel_value: label},)   # plot definieren. <b>...</b> fett geschrieben; <i>…</i> --> kursiv
    fig.update_layout(title_x=0.5,title_xanchor="center",title_font=dict(size=24))      # titel zentrieren und figure updaten
    #print(f"options sind: {options}")
    return (
        fig,
        fmt(min_speed, "m/s"),
        fmt(max_speed, "m/s"),
        fmt(avg_speed, "m/s"),
        fmt(total_dist, "m"),
        fmt_time(total_time_sec),
    )

if __name__ == "__main__":

    print("-------------------------------------------------")
    print(f"Dash-Server gestartet. Im Browser aufrufen über:")
    print(f"  -> http://127.0.0.1:{8050}")
    print(f"  oder (von anderem Gerät): http://<IP-deines-Rechners>:{8053}")
    print("-------------------------------------------------")
 	
    app.run(host="0.0.0.0", port=8050, debug=True)                  #debug=True setzt das Programm in debug-mode und ich muss nicht andauernd das Programm abbrechen und neu starten wenn ich was geändert habe, sondern es wird dauerhaft aktualisiert
    #app.run_server(debug=False, host="127.0.0.1", port=8050)
    # Vorgabe damit Programm remot gestartet werden kann.

