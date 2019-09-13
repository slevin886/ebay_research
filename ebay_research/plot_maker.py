import pandas as pd
import numpy as np
import os


def create_us_county_map(df):
    # Upload keys for zipcode to lat/lon location
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'zipcode_data.csv')
    zipcode_map = pd.read_csv(path)
    zipcode_map['zip'] = zipcode_map['zip'].astype(str)
    df = df.groupby('postalCode', as_index=False)['itemId'].count()
    df = pd.merge(df, zipcode_map, left_on='postalCode', right_on='zip').dropna()
    if df.shape[0] == 0:
        return None
    df['text'] = '# of Items: ' + df['itemId'].astype(str) + '<br>' + df['county_name'] + ' County, ' + df['state_id']
    return df.to_dict(orient='list')


COLORS = {'StoreInventory': 'blue', 'Auction': 'red', 'FixedPrice': 'green', 'AuctionWithBIN': 'yellow'}


def make_price_by_type(df):
    """
    Prepares traces for price by listing type scatter plot
    :param df: full dataframe
    :return: list of dictionaries representing different traces
    """
    df = df[['listingType', 'currentPrice_value']].copy()
    df = df.sort_values(by='listingType').reset_index(drop=True)
    data = []

    for i in df['listingType'].unique():
        sub = df.loc[df['listingType'] == i]
        trace = {'x': list(sub.index + 1), 'y': sub['currentPrice_value'].tolist(),
                 'mode': 'markers',
                 'name': i,
                 'showlegend': True,
                 'marker': {'color': [COLORS[i] for i in sub['listingType']],
                            'size': 10, 'line': {'color': 'black', 'width': 1.5}}}
        data.append(trace)

    return data


def make_sunburst(dic):
    labels = []
    parents = []
    values = []

    for key in dic.keys():
        labels.append(key)
        parents.append("")
        values.append(1)
        for name, count in dic[key].items():
            if name == 'Not Specified':
                labels.append(name + '<br>' + key)
            else:
                labels.append(name)
            parents.append(key)
            values.append(count)

    return [dict(type='sunburst', labels=labels, parents=parents, values=values,
                outsidetextfont={"size": 20, "color": "#377eb8"},
                marker={"line": {"width": 0.5, "color": "black"}})]


def prep_tab_data(df):
    """
    Isolates principal item categories for display in tabular data on home page
    :param df: full dataframe of ebay item data
    :return: dataframe
    """
    topics_for_tab = ['title', 'watchCount', 'galleryURL', 'viewItemURL',
                      'currentPrice_value', 'endTime']
    for topic in topics_for_tab:
        if topic not in df.columns:
            topics_for_tab.remove(topic)
    df = df[topics_for_tab].dropna(subset=['watchCount'])
    if df.empty:
        return None
    df = df.sort_values(by='watchCount', ascending=False)
    if 'endTime' in topics_for_tab:
        df['endTime'] = pd.to_datetime(df['endTime'])
    return df


def make_listing_pie_chart(listing_type):
    """

    :param listing_type: df['listingType'] from main frame
    :return:
    """
    listings = listing_type.value_counts()
    return [{'type': 'pie', 'labels': list(listings.index),
             'values': list(map(int, listings.values)),
             'hole': '0.4', 'marker': {'line': {'color': 'black', 'width': '2'}}}]
