import pandas as pd
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
    df = df[['listingInfo_listingType', 'currentPrice_value']].copy()
    df = df.sort_values(by='listingInfo_listingType').reset_index(drop=True)
    data = []

    for i in df.listingInfo_listingType.unique():
        sub = df.loc[df['listingInfo_listingType'] == i]
        trace = {'x': list(sub.index + 1), 'y': sub['currentPrice_value'].tolist(),
                 'mode': 'markers',
                 'name': i,
                 'showlegend': True,
                 'marker': {'color': [COLORS[i] for i in sub['listingInfo_listingType']],
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
    topics_for_tab = ['title', 'location', 'sellingStatus_bidCount', 'galleryURL', 'sellingStatus_timeLeft',
                      'viewItemURL', 'currentPrice_value', 'listingInfo_startTime', 'listingInfo_endTime',
                      'listingInfo_listingType']
    for topic in topics_for_tab:
        if topic not in df.columns:
            topics_for_tab.remove(topic)
    tab_data = df[topics_for_tab].copy()
    tab_data['listingInfo_startTime'] = pd.to_datetime(tab_data['listingInfo_startTime'])
    tab_data['listingInfo_endTime'] = pd.to_datetime(tab_data['listingInfo_endTime'])
    return tab_data


# def make_box_plot_prices(df):
#     prices = df[['currentPrice_value', 'listingInfo_endTime']]
#     prices['listingInfo_endTime'] = pd.to_datetime(prices['listingInfo_endTime'], utc=True)
#     prices['time_left'] = prices['listingInfo_endTime'] - datetime.now(tz=pytz.UTC)
#     prices['days'] = prices['time_left'].dt.days.astype(str)
#     prices = prices.sort_values(by='currentPrice_value')
#     return prices[['days', 'currentPrice_value']].copy()
