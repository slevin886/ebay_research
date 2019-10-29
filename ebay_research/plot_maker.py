import pandas as pd
import os

ZIP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'zipcode_data.csv')


def create_us_county_map(df):
    # Upload keys for zipcode to lat/lon location
    zipcode_map = pd.read_csv(ZIP_PATH)
    zipcode_map['zip'] = zipcode_map['zip'].astype(str)

    if df['postalCode'].str.contains('\*').sum() > 5:
        df['postalCode'] = df['postalCode'].str[:3]  # sometimes returns 3 digit zip codes
        zipcode_map['zip'] = zipcode_map['zip'].str[:3]
        zipcode_map = zipcode_map.drop_duplicates(subset=['zip'])

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
    df = df.sort_values(by='listingType').reset_index(drop=True)
    data = []

    for i in df['listingType'].unique():
        sub = df.loc[df['listingType'] == i]
        trace = {'x': list(sub.index + 1), 'y': sub['currentPrice_value'].tolist(),
                 'mode': 'markers',
                 'name': i,
                 'showlegend': True,
                 'marker': {'color': [COLORS[i] for i in sub['listingType']], 'opacty': 0.5,
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
    return df.to_dict(orient="records")


def make_listing_pie_chart(listing_type):
    """

    :param listing_type: df['listingType'] from main frame
    :return:
    """
    listings = listing_type.value_counts()
    return [{'type': 'pie', 'labels': list(listings.index),
             'values': list(map(int, listings.values)),
             'hole': '0.4', 'marker': {'line': {'color': 'black', 'width': '2'}}}]


def make_seller_bar(df):
    df['watchCount'] = df['watchCount'].fillna(0).astype(int)
    if 'feedbackScore' in df.columns:
        df['feedbackScore'] = df['feedbackScore'].astype(int)
        df = df.groupby('sellerUserName', as_index=False).agg({'feedbackScore': 'mean',
                                                               'watchCount': 'sum',
                                                               'categoryName': 'count'})
        df['feedbackScore'] = df['feedbackScore'].round(2).astype(str)
        df['watchCount'] = df['watchCount'].astype(str)
        df['hover'] = 'Total Feedback Score: ' + df['feedbackScore'] + '<br>Total Watch Count: ' + df['watchCount']
    else:
        df = df.groupby('sellerUserName', as_index=False).agg({'watchCount': 'sum', 'categoryName': 'count'})
        df['watchCount'] = df['watchCount'].astype(str)
        df['hover'] = '<br>Total Watch Count: ' + df['watchCount']
    df = df.sort_values(by='categoryName', ascending=False).head(10)
    return [{'x': df['sellerUserName'].tolist(), 'y': df['categoryName'].tolist(),
             'text': df['hover'].tolist(), 'type': 'bar',
             'marker': {'line': {'color': 'black', 'width': '2'}}
             }]


def make_auction_length(df):
    df['length'] = pd.to_datetime(df['endTime']) - pd.to_datetime(df['startTime'])
    df['length'] = df['length'].dt.days.astype(int)
    df = df.groupby('length', as_index=False)['endTime'].count()
    return [{'x': df['length'].tolist(), 'y': df['endTime'].tolist(),
             'type': 'bar', 'marker': {'line': {'color': 'black', 'width': '2'}, 'color': 'purple'}}]


def make_box_plot(df):
    df = df.pivot(columns='listingType', values='currentPrice_value')
    data = []

    for col in df.columns:
        sub = df[col].dropna().tolist()
        data.append(
            {'type': 'box', 'y': sub, 'name': col, 'boxpoints': False}
        )
    return data
