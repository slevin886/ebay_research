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
    df['text'] = '# of Items: ' + df['itemId'].astype(str) + '<br>' + df['county_name'] + ' County, ' + df['state_id']
    return df
