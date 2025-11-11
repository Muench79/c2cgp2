from dash import Dash, html

# Inizialisierung der Dash-App
app = Dash()

# Beipiel für das Erstellen eines Layouts der App ... 
# ... durch das Zusammenfügen verschiedener HTML-Komponenten
app.layout = html.Div(
    children=[
        html.H1(children='Eine Beispiel-App',
                style={'textAlign': 'center', 'marginTop': 40, 'marginBottom': 40}),
        html.H2(children='Wissenswertes'),    
        html.Div(children='Beispieltext. Dash ist ein tolles Ding!'),
    ]
)

# Starten der Dash-App
if __name__ == '__main__':
    print('**')
    app.run_server(debug=True) # Startet Server im Debug-Modus
