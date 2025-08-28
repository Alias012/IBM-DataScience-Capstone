# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = (pd.read_csv(
               "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv")
               .drop(columns='Unnamed: 0'))
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
options = [{'label': x, 'value': x} for x in spacex_df['Launch Site'].unique()]
options.insert(0, {'label': 'All Sites', 'value': 'ALL'})

# Create a dash application
app = dash.Dash(__name__)

app.title = 'SpaceX Dashboard'

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                             options=options,
                                             value='ALL',
                                             placeholder='Select a Launch Site',
                                             searchable=True),
                                html.Br(),

                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                dcc.RangeSlider(id='payload-slider',
                                                min=min_payload,
                                                max=max_payload,
                                                step=1000,
                                                value=[min_payload, max_payload]),

                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])


@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def update_pie(selected_site):
    if selected_site == 'ALL':
        return px.pie(data_frame=spacex_df.groupby('Launch Site')['class'].sum().reset_index(),
                      values='class',
                      names='Launch Site',
                      title='Number of Successes For All Sites')
    else:
        vals = spacex_df[spacex_df['Launch Site'] == selected_site]['class'].value_counts()
        return px.pie(
            values=vals.values,
            names=vals.index.map(lambda x: 'Successes' if x else 'Failures'),
            title=f'Successes vs Failures For {selected_site}')


@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id="payload-slider", component_property="value")])
def update_scatter(selected_site, payload_range):
    if selected_site == 'ALL':
        vals = spacex_df[spacex_df['Payload Mass (kg)'].between(payload_range[0], payload_range[1])]
        return px.scatter(data_frame=vals,
                          x='Payload Mass (kg)',
                          y='class',
                          color='Booster Version Category')
    else:
        vals = spacex_df[
            (spacex_df['Payload Mass (kg)'].between(payload_range[0], payload_range[1]))
            & (spacex_df['Launch Site'] == selected_site)]
        return px.scatter(data_frame=vals,
                          x='Payload Mass (kg)',
                          y='class',
                          color='Booster Version Category')


# Run the app
if __name__ == '__main__':
    app.run()