import pandas as pd
import numpy as np
from datetime import datetime
import pytz
import os


def create_us_county_map(df):
    # Upload keys for zipcode to lat/lon location
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'zipcode_data.csv')
    zipcode_map = pd.read_csv(path)
    zipcode_map['zip'] = zipcode_map['zip'].astype(str)
    df = df.groupby('postalCode', as_index=False)['itemId'].count()
    df = pd.merge(df, zipcode_map, left_on='postalCode', right_on='zip').dropna()
    if df.shape[0] < 2:
        return None
    df['text'] = '# of Items: ' + df['itemId'].astype(str) + '<br>' + df['county_name'] + ' County, ' + df['state_id']
    return df


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
    topics_for_tab = ['title', 'location', 'bidCount', 'galleryURL',
                      'viewItemURL', 'currentPrice_value', 'startTime', 'endTime',
                      'listingType']
    for topic in topics_for_tab:
        if topic not in df.columns:
            topics_for_tab.remove(topic)
    tab_data = df[topics_for_tab].copy()
    tab_data['startTime'] = pd.to_datetime(tab_data['startTime'])
    tab_data['endTime'] = pd.to_datetime(tab_data['endTime'])
    return tab_data


def summary_stats(df, largest_cat, largest_sub_cat):
    stats = dict()
    avg_price = str(df['currentPrice_value'].astype(float).mean().round(2))
    if len(avg_price.split('.')[-1]) < 2:
        avg_price = avg_price + '0'
    stats['avg_price'] = avg_price
    stats['returned_count'] = df.shape[0]
    stats['top_rated'] = np.round(df.loc[df['topRatedListing'] == 'true'].shape[0] / df.shape[0] * 100, 1)
    biggest_seller = df['sellerUserName'].value_counts()
    stats['top_seller'], stats['top_count'] = biggest_seller.idxmax(), biggest_seller.max()
    if largest_cat:
        stats['largest_cat_name'], stats['largest_cat_count'] = largest_cat[0], largest_cat[1]
    if largest_sub_cat:
        stats['largest_sub_name'], stats['largest_sub_count'] = largest_sub_cat[0], largest_sub_cat[1]
    return stats


# def make_box_plot_prices(df):
#     prices = df[['currentPrice_value', 'listingInfo_endTime']]
#     prices['listingInfo_endTime'] = pd.to_datetime(prices['listingInfo_endTime'], utc=True)
#     prices['time_left'] = prices['listingInfo_endTime'] - datetime.now(tz=pytz.UTC)
#     prices['days'] = prices['time_left'].dt.days.astype(str)
#     prices = prices.sort_values(by='currentPrice_value')
#     return prices[['days', 'currentPrice_value']].copy()
