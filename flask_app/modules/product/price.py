""" Functions related to a product's price"""

from flask_app.modules.extensions import DB, cache


@cache.memoize()
def has_pricerange(skuid):
    """Checks if the base product has variants with varying price points

    Often used to determine if a "Starting at" prefix (before the price) is necessary

    Args:
      skuid (str): The skuid of the product to check the pricerange for.

    Returns:
      bool: True = product variants with different prices, False = product has a single price
    """
    query = """
          SELECT id FROM options
          WHERE sku LIKE %(skuid_wildcard)s
          AND (pricechange+0) > 0
          LIMIT 1
      """
    result = DB.fetch_one(query, {"skuid_wildcard": skuid + "%"})
    if result and "id" in result:
        return True
    else:
        return False
