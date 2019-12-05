import pandas as pd
import os

# TODO: ensure that there are no null values being passed to JSON
# TODO: only bring necessary variables

ZIP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'zipcode_data.csv')
COLORS = {'StoreInventory': 'blue', 'Auction': 'red', 'FixedPrice': 'green', 'AuctionWithBIN': 'yellow'}


class MakePlots:

    def __init__(self, df, aspect_dict):
        self.df = df
        self.aspect_dict = aspect_dict
        self.results = dict()

    def run(self):
        tab_data, success = self.prep_tab_data()
        if success:
            self.results['tab_data'] = tab_data
        df_seller, success = self.make_seller_bar()
        if success:
            self.results['df_seller'] = df_seller
        map_plot, success = self.create_us_county_map()
        if success:
            self.results['map_plot'] = map_plot
        df_type, success = self.make_price_by_type()
        if success:
            self.results['df_type'] = df_type
        df_pie, success = self.make_listing_pie_chart()
        if success:
            self.results['df_pie'] = df_pie
        df_box, success = self.make_box_plot()
        if success:
            self.results['df_box'] = df_box
        hist_plot, success = self.create_hist_plot()
        if success:
            self.results['hist_plot'] = hist_plot
        if self.aspect_dict:
            sunburst_plot, success = self.make_sunburst()
            if success:
                self.results['sunburst_plot'] = sunburst_plot

    def create_hist_plot(self):
        if 'currentPrice_value' in self.df.columns:
            return self.df["currentPrice_value"].tolist(), True
        else:
            return list(), False

    def create_us_county_map(self):
        df = self.df.copy()
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
            return dict(), False
        df['text'] = '# of Items: ' + df['itemId'].astype(str) + '<br>' + df['county_name'] + ' County, ' + df['state_id']
        return df.to_dict(orient='list'), True

    def make_price_by_type(self):
        """
        Prepares traces for price by listing type scatter plot
        """
        df = self.df.copy()
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
        return data, True

    def make_sunburst(self):
        labels = []
        parents = []
        values = []

        for key in self.aspect_dict.keys():
            labels.append(key)
            parents.append("")
            values.append(1)
            for name, count in self.aspect_dict[key].items():
                if name == 'Not Specified':
                    labels.append(name + '<br>' + key)
                else:
                    labels.append(name)
                parents.append(key)
                values.append(count)

        return [dict(type='sunburst', labels=labels, parents=parents, values=values,
                    outsidetextfont={"size": 20, "color": "#377eb8"},
                    marker={"line": {"width": 0.5, "color": "black"}})], True

    def prep_tab_data(self):
        """
        Isolates principal item categories for display in tabular data on home page
        :param df: full dataframe of ebay item data
        :return: dataframe
        """
        df = self.df.copy()
        topics_for_tab = ['title', 'watchCount', 'galleryURL', 'viewItemURL',
                          'currentPrice_value', 'endTime']
        for topic in topics_for_tab:
            if topic not in df.columns:
                topics_for_tab.remove(topic)
        df = df[topics_for_tab].dropna(subset=['watchCount']).fillna('No Value Present')
        if df.empty:
            return dict(), False
        df['watchCount'] = df['watchCount'].astype(int)
        df = df.sort_values(by='watchCount', ascending=False)
        if 'endTime' in topics_for_tab:
            df['endTime'] = pd.to_datetime(df['endTime'])
        return df.to_dict(orient="records"), True

    def make_listing_pie_chart(self):
        """

        :param listing_type: df['listingType'] from main frame
        :return:
        """
        listing_type = self.df['listingType']
        listings = listing_type.value_counts()
        return [{'type': 'pie', 'labels': list(listings.index),
                 'values': list(map(int, listings.values)),
                 'hole': '0.4', 'marker': {'line': {'color': 'black', 'width': '2'}}}], True

    def make_seller_bar(self):
        df = self.df.copy()
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
                 }], True

    def make_box_plot(self):
        df = self.df.copy()
        # df = df.reset_index(drop=True)
        df = df.pivot(columns='listingType', values='currentPrice_value')
        data = []

        for col in df.columns:
            sub = df[col].dropna().tolist()
            data.append(
                {'type': 'box', 'y': sub, 'name': col, 'boxpoints': False}
            )
        return data, True
