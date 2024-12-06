""" Functions related to preloading data (usually from cache) to use in the request context """

from flask import current_app
from datetime import datetime
from flask_app.modules.extensions import DB, cache
from flask_app.modules.helpers import split_to_list, split_and_quote


@cache.memoize()
def get_preload_data():
    """Load a dictionary of data so it's available in the cache for the request context

    Returns:
      dict: Various data collections
    """

    return {
        "product_promo": get_product_promo_values(),
        "categories_products": get_categories_products(),
        "gdiscounts": get_gdiscounts(),
        "discounts": get_discounts(),
        "product_specials": get_product_specials(),
        "shipping_rates": get_shipping_rates(),
        "promo_exclude": get_promo_exclusions(),
        "source_codes": get_source_codes(),
        "vendor_search": get_search_state(),
    }

@cache.memoize()
def get_categories_products():
    """Category code -> products relationship used for category promotions

    Returns:
      dict: A dictionary where the key is the category code and the value is a list of
        the products in that category
    """

    categories_products = {}

    query = DB.fetch_all("SELECT DISTINCT(category_code) AS category_code FROM products_to_categories_loop")
    for row in query["results"]:
        categories_products[row["category_code"]] = []
        inner = DB.fetch_all(
            "SELECT skuid from products_to_categories_loop WHERE category_code = %(category_code)s",
            {"category_code": row["category_code"]},
        )
        for ref in inner["results"]:
            categories_products[row["category_code"]].append(ref["skuid"])

    return categories_products

@cache.memoize()
def get_gdiscounts():
    """data for quantity and group discounts.

    Returns:
      dict: The 'index' key is a list of all SKUs that have active gdiscounts (for easy lookup)
            The 'data' key is a list of the discounts themselves
    """

    gdiscounts = {"index": [], "data": []}
    gdiscount_query = DB.fetch_all("""
      SELECT product_group, group_type, quantity, discount, discount_type
      FROM gdiscounts
      WHERE start_timestamp <= NOW()
      AND end_timestamp > NOW()
    """)

    if gdiscount_query["results"]:
        for row in gdiscount_query["results"]:
          skus = []

          # group_type "1" is a list of SKUs
          if row['group_type'] == 1:
            skus = split_to_list(row["product_group"])

          # group_type "2" is a category or list of categories
          elif row['group_type'] == 2:
            codes = split_to_list(row["product_group"])
            if not codes:
              continue
            skus = DB.fetch_all(
                """
                  SELECT skuid
                  FROM products_to_categories_loop
                  WHERE category_code IN %(category_codes)s
                  GROUP BY skuid
                """,
                {"category_codes": tuple(codes)},
            )["results"]
            skus = [i["skuid"] for i in skus]

          # group_type "3" is a list of CLEARANCE_SPECIAL values
          elif row['group_type'] == 3:
            target_values = split_to_list(row["product_group"])
            if not target_values:
              continue
            cached_promo_values = get_product_promo_values()
            for val in target_values:
              for i in cached_promo_values["data"]:
                if i["value"] == val:
                  skus.append(i["skuid"])

          if not skus:
            continue

          #current_app.logger.debug(f"skus: {skus}")

          gdiscounts["data"].append(
              {
                  "skuids": skus,
                  "quantity": row["quantity"],
                  "discount": float(row["discount"]),
                  "discount_type": int(row["discount_type"]),
              }
          )
          for sku in skus:
              if sku not in gdiscounts["index"]:
                  gdiscounts["index"].append(sku)

    return gdiscounts

@cache.memoize()
def get_discounts():
    """Data for general discounts

    Consult 'discounts' table column names which are the keys on the objects

    Returns:
      dict: the 'index' key contains a list of coupon codes, uppercased (for easy lookup)
            the 'data' key contains the promotions themselves

    """
    discounts = {"index": [], "data": []}
    discount_query = DB.fetch_all(
        """
      SELECT *
      FROM discounts
      WHERE (code IS NOT NULL AND code != '')
      AND (discount IS NOT NULL AND discount != '')
      ORDER BY id ASC
    """
    )

    if discount_query["results"]:
        discounts["data"] = discount_query["results"]
        for row in discounts["data"]:
            row["code"] = row["code"].strip().upper()  # uppercase coupon codes to normalize
            if row["code"] not in discounts["index"]:
                discounts["index"].append(row["code"].strip().upper())

    # current_app.pp.pprint(discounts)
    return discounts

@cache.memoize()
def get_product_specials():
    """A product special an product that is on sale for a specified time

    Returns:
      dict: the 'index' key contains a list of SKUs with specials
            the 'data' key contains the promotions themselves
    """

    product_specials = {"index": [], "data": []}
    specials_query = DB.fetch_all(
        """
      SELECT * FROM
      weekly_specials
      WHERE start_date <= NOW()
      AND end_date >= NOW()
      GROUP BY skuid
    """
    )

    if specials_query["results"]:
        for row in specials_query["results"]:
            product_specials["data"].append({"skuid": row["skuid"], "special_price": row["daily_special_price"]})
            if row["skuid"] not in product_specials["index"]:
                product_specials["index"].append(row["skuid"])

    return product_specials

@cache.memoize()
def get_product_promo_values():
    """products can be "tagged" with a values in CLEARANCE_SPECIAL
    and allows promo groups to be created.  like "%10 of selected items"
    The CLAERANCE_SPECIAL can be a semicolon-delimited list

    Returns:
      dict: the 'index' key contains a list of SKUs with promo values
            the 'data' key contains the promotions themselves
    """

    product_promo = {"index": [], "data": []}
    promo_query = DB.fetch_all(
        """
          SELECT SKUID,CLEARANCE_SPECIAL
          FROM products
          WHERE (CLEARANCE_SPECIAL IS NOT NULL AND CLEARANCE_SPECIAL != '')
        """
    )

    if promo_query["results"]:
        for row in promo_query["results"]:
            for val in split_to_list(row["CLEARANCE_SPECIAL"]):
                product_promo["data"].append(
                    {
                        "skuid": row["SKUID"],
                        "value": val,
                    }
                )
                if row["SKUID"] not in product_promo["index"]:
                    product_promo["index"].append(row["SKUID"])

    return product_promo

@cache.memoize()
def get_source_codes():
    """creates a list of valid source codes.  While employee discount codes
    are not considered true "source codes", the site handles them that way
    to allow for promotion "stacking" (use of a promotional source code and a coupon code)

    Returns:
      list: A list of valid source codes
    """

    source_codes = [i["code"] for i in current_app.config["EMPLOYEE_DISCOUNTS"]]
    q = DB.fetch_all("SELECT code FROM source_codes")
    if q and "results" in q:
        source_codes.extend([i["code"] for i in q.get("results")])

    return source_codes

@cache.memoize()
def get_promo_exclusions():
    """Create a list of skus that are excluded from promotions

    Returns:
      list: a list of base SKUs
    """

    res = DB.fetch_all("SELECT SKUID FROM products WHERE PROMO_EXCLUDE = '1'")["results"]
    exclude = [i["SKUID"] for i in res]
    exclude.append("GC9999")
    exclude.append("EC9999")
    return exclude

@cache.memoize()
def get_shipping_rates():
    """
    Loads data from the shipping chart

    Returns:
      list: A list of dictionaries, each being a price tier in the shipping chart
    """

    rates = DB.fetch_all("SELECT * from standard_rates_loop ORDER BY order_min ASC")["results"]

    # check for a 0.00 tier, if there isn't one, add it
    zero_tier = next((i for i in rates if i["order_min"] == 0.00), None)

    if not zero_tier:
        base_tier = next((i for i in rates if i["order_min"] == 0.01))
        rates.append(
            {
                "id": 0,
                "order_min": 0.00,
                "order_max": 0.00,
                "shipping_cost": 0.00,
                "rush": base_tier["rush"] - base_tier["shipping_cost"],
                "2day": base_tier["2day"] - base_tier["shipping_cost"],
                "overnight": base_tier["overnight"] - base_tier["shipping_cost"],
                "canada": base_tier["canada"] - base_tier["shipping_cost"],
                "modifier": "+",
            }
        )

    return rates


@cache.memoize()
def get_flip_catalog():
    """Get current virtual catalog data from flip_catalog.

    Returns:
      dict: A dctionary containing drop_name, dop_link, drop_code
    """

    return DB.fetch_one(
        """
          SELECT drop_name, drop_link, drop_code
          FROM flip_catalog
          ORDER BY id DESC LIMIT 1
        """
    )

@cache.memoize()
def get_search_state():
    """Gets the current state of the vendor search provider.  If off, the search and category functionality
    is very basic.  for use when the provider (like searchspring) is down.

    Returns:
      bool: True if vendor search is on, false if not
    """

    vendor_search = True
    q = DB.fetch_one(
        """
            SELECT `state` FROM site_control
            WHERE service = 'vendor_search'
        """
    )
    if q and q["state"] == "off":
        vendor_search = False

    return vendor_search
