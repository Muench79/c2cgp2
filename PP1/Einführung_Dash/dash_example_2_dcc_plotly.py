from dash import Dash, dcc, html

import plotly.express as px
df = px.data.stocks()
fig = px.line(df, x=df['date'], y=df['GOOG'])

app = Dash()

app.layout = html.Div(
    children=[
        html.H1(children='Zeitreihe Aktie Google'),
        dcc.Graph(figure=fig) # Graph-Komponente 
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True)
