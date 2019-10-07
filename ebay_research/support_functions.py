from flask import request, session


def ingest_free_search_form(form):
    final = dict()
    final['keywords'] = form.keywords_include.data.strip()
    final['excluded_words'] = form.keywords_exclude.data.strip()
    final['min_price'] = form.minimum_price.data
    final['max_price'] = form.maximum_price.data
    final['sort_order'] = request.form.get("item_sort")
    final['listing_type'] = request.form.get("listing_type")
    final['item_condition'] = request.form.get("condition")
    return final


def currency_maker(dollars: float):
    return '{:.2f}'.format(dollars)


BOOL_MAP = {'true': True, 'false': False}


def summary_stats(df, largest_cat, largest_sub_cat, total_items_available):
    stats = dict()
    stats['avg_price'] = currency_maker(df['currentPrice_value'].astype(float).mean())
    stats['median_price'] = currency_maker(df['currentPrice_value'].astype(float).median())
    stats['avg_shipping_price'] = currency_maker(df['shippingServiceCost_value'].astype(float).mean())
    stats['total_watch_count'] = int(df['watchCount'].fillna(0).astype(int).sum())
    stats['returned_count'] = int(df.shape[0])
    stats['top_rated_percent'] = round(df['topRatedSeller'].map(BOOL_MAP).mean() * 100, 2)
    stats['top_rated_listing'] = round(df['topRatedListing'].map(BOOL_MAP).mean() * 100, 2)
    biggest_seller = df['sellerUserName'].value_counts()
    stats['top_seller'], stats['top_seller_count'] = biggest_seller.idxmax(), int(biggest_seller.max())
    if total_items_available:
        stats['total_entries'] = int(total_items_available)
    if largest_cat:
        stats['largest_cat_name'], stats['largest_cat_count'] = largest_cat[0], int(largest_cat[1])
        session['largest_cat_name'], session['largest_cat_count'] = stats['largest_cat_name'], stats['largest_cat_count']
    if largest_sub_cat:
        stats['largest_sub_name'], stats['largest_sub_count'] = largest_sub_cat[0], int(largest_sub_cat[1])
        session['largest_sub_name'], session['largest_sub_count'] = stats['largest_sub_name'], stats['largest_sub_count']
    return stats
