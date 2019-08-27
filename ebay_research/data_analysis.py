import pandas as pd
from ebaysdk.exception import ConnectionError
from ebaysdk.finding import Connection as Finding


# TODO: Separate collection of category and aspect data from test_function
# TO Support In Future:
# findItemsByCategory
# Eventually use this: 'GetCategoryInfo' to get valid category ids
# findItemsByCategory (max: 3, will need to be specified separately for each one i)
# search variation:
# baseball card  (both words) baseball,card (exact phrase baseball card)
# (baseball,card) (items with either baseball or card)  baseball -card (baseball but NOT card)
# baseball -(card,star) (baseball but NOT card or star)


class EasyEbayData:

    def __init__(self, api_id: str, keywords: str, excluded_words: str = None, sort_order: str = "BestMatch",
                 search_type: str = "findItemsByKeywords", wanted_pages: int = None, listing_type: str = None,
                 usa_only: bool = True, min_price: float = 0.0, max_price: float = None,
                 item_condition: str = None):
        """
        A class that returns a clean data set of items for sale based on a keyword search from ebay
        :param api_id: eBay developer app's ID
        :param keywords: Keywords should be between 2 & 350 characters, not case sensitive
        :param wanted_pages: The number of desired pages to return w/ 100 items per page
        :param search_type: Search type, for now only findItemsByKeywords accepted
        :param listing_type: A string for listing type (Auction, etc.) or None to search all
        :param item_condition: A string representing the item condition code
        """
        self.api = Finding(appid=api_id, config_file=None)
        self.search_type = search_type
        self.keywords = keywords  # keywords only search item titles
        self.exclude_words = excluded_words
        self.wanted_pages = wanted_pages  # must be at least 1 & integer
        self.usa_only = True if usa_only else False
        self.min_price = min_price if min_price else 0.0
        self.max_price = max_price
        self.sort_order = sort_order
        self.listing_type = listing_type
        self.item_condition = item_condition
        self.search_url = None  # will be the result url of the first searched page
        self.item_aspects = None  # dictionary of item features
        self.category_info = None  # dictionary of category id and subcategories
        self.largest_sub_category = None
        self.largest_category = None
        self.total_pages: int = None  # the total number of available pages
        self.total_entries: int = None  # the total number of items available given keywords (all categories)
        if excluded_words and len(excluded_words) > 2:
            excluded_words = ",".join(word for word in excluded_words.split(" "))
            self.full_query = keywords + " -(" + excluded_words + ")"
        else:
            self.full_query = keywords
        self.item_filter = self._create_item_filter()

    def _create_item_filter(self):
        if self.sort_order in ['BidCountMost', 'BidCountFewest']:
            if self.listing_type not in ['Auction', 'AuctionWithBIN']:
                print("Changing listing type to auction to support a sort order using bid count")
                self.listing_type = 'Auction'  # sort order without that listing type returns nothing
        item_filter = list()
        item_filter.append({'name': 'MinPrice', 'value': self.min_price})
        if self.max_price and self.max_price > self.min_price:
            item_filter.append({'name': 'MaxPrice', 'value': self.max_price})
        if self.listing_type:
            item_filter.append({'name': 'ListingType', 'value': self.listing_type})
        if self.item_condition:
            item_filter.append({'name': 'Condition', 'value': self.item_condition})
        if self.usa_only:
            item_filter.append({'name': 'LocatedIn', 'value': 'US'})
        return item_filter

    def flatten_dict(self, item, acc=None, parent_key='', sep='_'):
        """
        The ebay API returns items as nested dictionaries, this recursive function flattens them
        :param item: dictionary for individual item
        :param acc: a dictionary that is used to pass through keys
        :param parent_key: nested parent key in dictionary
        :param sep: separates parent & nested keys if necessary
        :return: flat item dictionary
        """
        double_keys = ('_currencyId', 'value')  # known doubles where want always show parent key
        final = dict() if acc is None else acc
        for key, val in item.items():
            if isinstance(val, dict):
                self.flatten_dict(val, final, parent_key=key)
            else:
                if key in final or key in double_keys:
                    final[parent_key + sep + key] = val
                else:
                    final[key] = val
        return final

    def get_category_info(self, category):
        """
        Executes once from the test connection function to retrieve the categories that returned items
        belong to. Also sets attributes that reveal largest category and sub category.
        :param category: response['categoryHistogramContainer'] from the response dictionary object
        :return: Dictionary of categories and their counts
        """
        try:
            largest = category['categoryHistogram'][0]
            self.largest_category = [largest['categoryName'], largest['count']]
            sub = largest['childCategoryHistogram'][0]
            self.largest_sub_category = [sub['categoryName'], sub['count']]
        except (IndexError, KeyError):
            print('No subcategories for search')
            pass
        clean_categories = {}
        for cat in category['categoryHistogram']:
            clean_categories[cat['categoryName']] = {'categoryId': cat['categoryId'], 'count': cat['count']}
        return clean_categories

    @staticmethod
    def clean_aspect_dictionary(aspects):
        """
        There is also a second key 'domainDisplayName' for these aspects
        :param aspects:
        :return:
        """
        all_aspects = {}
        for asp in aspects['aspect']:
            sub_aspect = {}
            for name in asp['valueHistogram']:
                sub_aspect[name['_valueName']] = int(name['count'])
            all_aspects[asp['_name']] = sub_aspect
        return all_aspects

    def _test_connection(self):
        """Tests that an initial API connection is successful"""
        try:
            response = self.api.execute(self.search_type, {'keywords': self.full_query,
                                                           'paginationInput': {'pageNumber': 1,
                                                                               'entriesPerPage': 100},
                                                           'itemFilter': self.item_filter,
                                                           'sortOrder': self.sort_order,
                                                           'outputSelector': ['SellerInfo', 'StoreInfo',
                                                                              'AspectHistogram', 'CategoryHistogram']
                                                           })
            assert response.reply.ack == 'Success'
            print('Successfully Connected to API!')
            response = response.dict()
            if response['paginationOutput']['totalPages'] == '0':
                print(f'There are no results for a search of: {self.full_query}')
                return "no_results_error"
            self.search_url = response['itemSearchURL']
            # Not all searches, particularly empty searches, have subcategories/item aspects
            try:
                self.category_info = self.get_category_info(response['categoryHistogramContainer'])
            except KeyError:
                print(f'There are no categories for a search of: {self.full_query}')
            try:
                self.item_aspects = self.clean_aspect_dictionary(response['aspectHistogramContainer'])
            except KeyError:
                print(f'There are no aspects for a search of: {self.full_query}')
            return response
        except ConnectionError:
            print('Connection Error! Ensure that your API key was correctly entered.')
            return "connection_error"
        except AssertionError:
            print(f'There are no results for a search of: {self.full_query}')
            return "no_results_error"

    def _get_wanted_pages(self, response):
        """response comes from test_connection to access total pages without making another API call"""
        self.total_pages = int(response['paginationOutput']['totalPages'])
        self.total_entries = int(response['paginationOutput']['totalEntries'])
        if self.wanted_pages:
            # can't pull more than max pages
            pages2pull = min([self.total_pages, self.wanted_pages])
        else:
            pages2pull = self.total_pages
        return pages2pull

    def get_data(self):
        all_items = []

        response = self._test_connection()

        if response in ["connection_error", "no_results_error"]:
            return response

        # Add initial items from test
        data = response['searchResult']['item']

        all_items.extend([self.flatten_dict(i) for i in data])
        pages2pull = self._get_wanted_pages(response)

        if pages2pull < 2:  # stop if only pulling one page or only one page exists
            return pd.DataFrame(all_items)

        total_errors = 0

        for page in range(2, pages2pull + 1):
            response = self.api.execute(self.search_type, {'keywords': self.full_query,
                                                           'paginationInput': {'pageNumber': page,
                                                                               'entriesPerPage': 100},
                                                           'itemFilter': self.item_filter,
                                                           'sortOrder': self.sort_order,
                                                           'outputSelector': ['SellerInfo', 'StoreInfo']
                                                           })
            if response.reply.ack == 'Success':
                data = response.dict()['searchResult']['item']
                all_items.extend([self.flatten_dict(i) for i in data])

            else:
                print('Unable to connect to page #: ', page)
                total_errors += 1
                if total_errors == 2:
                    print('API limit reached or pull finished. Pulled {} pages'.format(page - 2))
                    return pd.DataFrame(all_items)

        return pd.DataFrame(all_items)
