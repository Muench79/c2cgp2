
#Sicherheitsklausel
 #   app.run(debug=True) # Lässt APP starten debug=True lässte Fehler anzeigen
from dash import Dash, html, dcc, Input, Output #Schablone für Website
#from basecar import BaseCar
app = Dash(__name__) #Name der APP

app.layout = html.Div(
    [
        html.H1("Hallo Projektphase 1", id="h-1"),
        dcc.Slider(min=0, max=10),
        dcc.Dropdown(options=["Hallo", "Tschüss"], value="hallo", id="dd-1"),
        dcc.Dropdown(options=["Ingo", "Johanna"], value="hallo", id="dd-2")
    ]
)
@app.callback(
    Output("h-1", "children"),
    Input("dd-1", "value"),
    Input("slider-1", "value")
)


def change_greeting(in1, in2):
    return f"{in1, in2} du!"

app.callback(
   Output("h-1", "children", allow_duplicate=True),
   Input("dd-2", "value"),
   prevent_initial_call=True
)
def change_name(in1):
    return f"{in1} test!"  
    


if __name__ == "__main__": # -blauer Buttom
    app.run(host="0.0.0.0", port=8051, debug=True) 
#Host 0.0.0 alle Geräte dürfen zugreifen wenn IP 
# gesetzt ist kann nur die gesetzte IP zugreifen
    
