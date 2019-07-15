import plotly as py
import plotly.graph_objs as go
import pandas as pd
import os


def create_us_county_map(df):
    df = df.groupby('postalCode', as_index=False)['itemId'].count()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'zipcode_data.csv')
    zipcode_map = pd.read_csv(path)
    zipcode_map['zip'] = zipcode_map['zip'].astype(str)
    # the command below is inner and drops nulls, probably want to collect this later
    df = pd.merge(df, zipcode_map, left_on='postalCode', right_on='zip').dropna()
    if df.shape[0] < 2:
        return None
    df['text'] = 'items: ' + df['itemId'].astype(str) + '<br>' + df['county_name'] + ' County, ' + df['state_id']
    data = [go.Scattergeo(locationmode='USA-states', lon=df['lng'], lat=df['lat'],
                          text=df['text'], mode='markers',
                          marker=dict(size=df['itemId'],
                                      sizemode='area',
                                      sizeref=2. * max(df['itemId']) / (40. ** 2),
                                      sizemin=4,
                                      opacity=0.8,
                                      autocolorscale=True,
                                      line=dict(width=1, color='rgba(102, 102, 102)'),
                          cmin=0,
                          color=df['itemId'],
                          cmax=df['itemId'].max(),
                          colorbar=dict(title="<strong>Number of Items</strong>")))]

    layout = dict(
        margin=dict(r=0, t=0, b=0, l=0),
        geo=dict(
            scope='usa',
            projection=dict(type='albers usa'),
            showland=True,
            landcolor="rgb(250, 250, 250)",
            subunitcolor="rgb(217, 217, 217)",
            countrycolor="rgb(217, 217, 217)",
            countrywidth=0.5,
            subunitwidth=0.5
        ),
    )
    return py.offline.plot({'layout': layout, 'data': data},
                           config=dict(modeBarButtonsToRemove=['sendDataToCloud'], showLink=False,
                                       displayModeBar=False, displaylogo=False),
                           output_type="div", include_plotlyjs=False)
