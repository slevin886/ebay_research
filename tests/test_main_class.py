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
    assert ebay_data.total_entries is None
    assert ebay_data.item_aspects is None
    assert ebay_data.max_price is None
    with pytest.raises(TypeError):
        assert EasyEbayData(), "can't initialize empty class"


def test_create_item_filter():
    """Tests the _create_item_filter method"""
    ebay_data = EasyEbayData(api_id=API_ID, keywords='test item filter', sort_order='BidCountMost',
                             max_price=72, min_price=10, item_condition='used')
    test_filter = ebay_data.item_filter
    assert len(test_filter) == 5, "not all expected item filters are present"
    filter_names = set()
    filter_values = set()
    for filter in test_filter:
        assert 'name' in filter, "missing necessary key 'name'"
        assert 'value' in filter, "missing necessary key 'value'"
        filter_names.add(filter['name'])
        filter_values.add(filter['value'])
    assert filter_names == {'MinPrice', 'MaxPrice', 'ListingType', 'Condition', 'LocatedIn'}, 'wrong filters present'
    assert filter_values == {10, 72, 'Auction', 'used', 'US'}, 'wrong values present'


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


def test_clean_aspect_dictionary():
    fake_aspects = {'aspect': {'domainDisplayName': 'aspect subject',
                               'aspect': [
                                    {'valueHistogram': [
                                        {'count': '1', '_valueName': 'val1'},
                                        {'count': '1', '_valueName': 'val2'},
                                    ],
                                     '_name': 'name1'},
                                    {'valueHistogram': [
                                        {'count': '2', '_valueName': 'val3'},
                                        {'count': '2', '_valueName': 'val4'}
                                    ],
                                     '_name': 'name2'}
                               ]
                               }
                    }
    ebay_data = EasyEbayData(api_id=API_ID, keywords="test class")
    test_results = ebay_data.clean_aspect_dictionary(fake_aspects)
    assert 'name1' in test_results.keys(), 'aspect names should be present in keys'
    assert 'name2' in test_results.keys(), 'aspect names should be present in keys'
    assert 'val1' in test_results['name1'].keys(), '_name values should be nested keys'
    assert isinstance(test_results['name1']['val1'], int), 'string counts should be converted to integers'
    assert test_results['name2']['val3'] == 2, 'aspect counts should be values to _valueName key'
