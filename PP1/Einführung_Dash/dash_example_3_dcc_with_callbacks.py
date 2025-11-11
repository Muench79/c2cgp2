from dash import Dash,dcc,html
from dash.dependencies import Input, Output
import plotly.express as px
df = px.data.stocks()
app = Dash()

#Layoutbeschreibung mit Id's und Dropout-Element
app.layout = html.Div(
    children=[
        html.H3(id='title',children='Aktienkurse'),
        dcc.Dropdown(id='dropdown',
                     options=[
                         {'label': 'Google', 'value': 'GOOG'},
                         {'label': 'Apple', 'value': 'AAPL'},
                         {'label': 'Amazon', 'value': 'AMZN'},
                     ],
                     value='GOOG'),
        dcc.Graph(id='line_plot'),
    ]
)

# Callback erklärt Funktionalität des Dropdown-Element
@app.callback(Output(component_id='line_plot', component_property='figure'),
              Input(component_id='dropdown', component_property='value'))
def graph_update(value_of_input_component):
    print(value_of_input_component)
    fig = px.line(df, x=df['date'], y=df[value_of_input_component])
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
