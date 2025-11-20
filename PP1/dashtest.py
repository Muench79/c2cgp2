from dash import Dash, html, Output, Input
from dash_extensions import EventListener

app = Dash(__name__)

# EventListener für mousedown und mouseup
listener = EventListener(
    html.Button("Auto steuern", id="auto-button"),
    events=[{"event": "mousedown", "props": ["type"]},
            {"event": "mouseup", "props": ["type"]}],
    id="event-listener"
)

app.layout = html.Div([
    listener,
    html.Div(id="status")
])

@app.callback(
    Output("status", "children"),
    Input("event-listener", "event")
)
def handle_event(e):
    if e is None:
        return "Bereit"
    if e["type"] == "mousedown":
        return "🚗 Auto fährt los!"
    elif e["type"] == "mouseup":
        return "🛑 Auto stoppt!"
    return "Unbekanntes Ereignis"

if __name__ == "__main__":
    app.run_server(host='0.0.0.0'debug=True)
