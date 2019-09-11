import pytest
import os
from ebay_research.data_analysis import EasyEbayData

API_ID = os.environ.get(
    "EBAY_API"
)  # Must set your eBay API ID as an environmental variable


def test_class_init():
    """Assert that EasyEbayData class initialization executes as expected"""
    ebay_data = EasyEbayData(
        api_id=API_ID,
        keywords="electric guitar",
        excluded_words="fender",
        sort_order="BidCountMost",
    )
    assert (
        ebay_data.full_query == "electric guitar -(fender)"
    ), "not excluding words correctly"
    assert ebay_data.sort_order == "BidCountMost"
    assert ebay_data.min_price == 0.0
    assert (
        ebay_data.listing_type == "Auction"
    ), "Choosing a sort order with bid count should make this auction"
    assert (
        len(ebay_data.item_filter) == 3
    ), "Here, here should be 3 item filters (min_price, listing_type, located_in)"
    # should have None values
    assert ebay_data.wanted_pages is None
    assert ebay_data.total_entries is None
    assert ebay_data.item_aspects is None
    assert ebay_data.max_price is None
    with pytest.raises(TypeError):
        assert EasyEbayData(), "can't initialize empty class"



    # def _create_item_filter(self):
    #     if self.sort_order in ['BidCountMost', 'BidCountFewest']:
    #         if self.listing_type not in ['Auction', 'AuctionWithBIN']:
    #             print("Changing listing type to auction to support a sort order using bid count")
    #             self.listing_type = 'Auction'  # sort order without that listing type returns nothing
    #     item_filter = list()
    #     item_filter.append({'name': 'MinPrice', 'value': self.min_price})
    #     if self.max_price and self.max_price > self.min_price:
    #         item_filter.append({'name': 'MaxPrice', 'value': self.max_price})
    #     if self.listing_type:
    #         item_filter.append({'name': 'ListingType', 'value': self.listing_type})
    #     if self.item_condition:
    #         item_filter.append({'name': 'Condition', 'value': self.item_condition})
    #     if self.usa_only:
    #         item_filter.append({'name': 'LocatedIn', 'value': 'US'})
    #     return item_filter


def test_create_item_filter():
    """Tests the _create_item_filter method"""
    ebay_data = EasyEbayData(api_id=API_ID)
    # TODO: continue building from here


def test_flatten_dict():
    """Tests the flatten_dict method to flatten dictionaries"""
    dict2flatten = {
        "a": {"b": 1, "c": {"b": 1, "d": 1}},
        "c": 1,
        "e": 1,
        "f": {"value": 1},
    }
    solution = {
        "b": 1,
        "c_b": 1,
        "d": 1,
        "c": 1,
        "e": 1,
        "f_value": 1,
    }  # value is duplicate should always have parent
    ebay_data = EasyEbayData(api_id=API_ID, keywords="test class")
    assert (
        ebay_data.flatten_dict(dict2flatten) == solution
    ), "should flatten dic and join variable only where necessary"


def test_clean_category_info():
    category2clean = {
        "categoryHistogram": [
            {
                "categoryId": "1",
                "categoryName": "test_data_1",
                "count": "1",
                "childCategoryHistogram": [
                    {"categoryId": "3", "categoryName": "test_child", "count": "1"}
                ],
            },
            {
                "categoryId": "2",
                "categoryName": "test_data_2",
                "count": "1",
                "childCategoryHistogram": [
                    {"categoryId": "4", "categoryName": "test_child_2", "count": "1"}
                ],
            },
        ]
    }
    solution = {'test_data_1': {'categoryId': '1', 'count': '1'}, 'test_data_2': {'categoryId': '2', 'count': '1'}}
    ebay_data = EasyEbayData(api_id=API_ID, keywords="test class")
    clean_category = ebay_data.clean_category_info(category2clean)
    assert clean_category == solution, 'should pull all categories, ids, counts'
    assert ebay_data.largest_sub_category == ['test_child', '1'], 'sets largest sub category as attribute'
    assert ebay_data.largest_category == ['test_data_1', '1'], 'set largest category as attribute'

