import pytest
import os
from ebay_research.data_analysis import EasyEbayData

API_ID = os.environ.get('EBAY_API')  # Must set your eBay API ID as an environmental variable


def test_class_init():
    """Assert that EasyEbayData class initialization executes as expected"""
    ebay_data = EasyEbayData(api_id=API_ID, keywords='electric guitar', excluded_words='fender',
                             sort_order='BidCountMost')
    assert ebay_data.full_query == 'electric guitar -(fender)', 'not excluding words correctly'
    assert ebay_data.sort_order == 'BidCountMost'
    assert ebay_data.min_price == 0.0
    assert ebay_data.listing_type == 'Auction', 'Choosing a sort order with bid count should make this auction'
    assert len(ebay_data.item_filter) == 3, 'Here, here should be 3 item filters (min_price, listing_type, located_in)'
    # should have None values
    assert ebay_data.wanted_pages is None
    assert ebay_data.total_entries is None
    assert ebay_data.item_aspects is None
    assert ebay_data.max_price is None
    with pytest.raises(TypeError):
        assert EasyEbayData(), "can't initialize empty class"


def test_flatten_dict():
    """Tests the flatten_dict function to flatten dictionaries"""
    dict2flatten = {'a': {'b': 1, 'c': {'b': 1, 'd': 1}}, 'c': 1,  'e': 1}
    solution = {'b': 1, 'c_b': 1, 'd': 1, 'c': 1, 'e': 1}
    ebay_data = EasyEbayData(api_id=API_ID, keywords='test class')
    assert ebay_data.flatten_dict(dict2flatten) == solution, 'should flatten dic and join variable only where necessary'
