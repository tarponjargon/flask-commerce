""" Functions related to a product's metadata attributes """

from flask import current_app
from flask_app.modules.extensions import DB, cache
from flask_app.modules.helpers import is_number

def get_drop_ship(drop_ship_code=0):
    """Get a product's drop ship message

    Args:
      drop_ship_code (int): The code (stored on the product record)

    Returns:
      dict:
        id (int): the drop ship code
        description (str): Description of the drop ship type

    """
    if not drop_ship_code or not is_number(drop_ship_code):
        drop_ship_code = 0

    dropship = {"id": drop_ship_code, "description": ""}

    result = DB.fetch_one("SELECT id, description FROM drop_ship_type WHERE id = %(code)s", {"code": drop_ship_code})
    if result:
        dropship = result

    return dropship


def get_alternate_ids(base_skuid):
    """get alternate part numbers for the item

    Args:
      base_skuid (str): THe base SKUID for the item to look up
      NOTE: I am using LIKE to partial match the base skuid to the
      google_feed.id field (the fullsku) because there is a rule
      in the google feed generator that some items have the
      item_group_id suppressed

    Returns:
      dict:
        mpn: list of all manufacturer's part numbers for product
        gtin: list of all associated GTINs for products
        brand: product brand
    """

    ids = {"mpn": [], "gtin": [], "brand": current_app.config["STORE_NAME"] }

    if not base_skuid or not isinstance(base_skuid, str) or len(base_skuid) < 4:
      return ids

    q = DB.fetch_all(
        """
          SELECT brand, gtin, mpn
          FROM google_feed
          WHERE id LIKE %(base_skuid)s
        """,
        {"base_skuid": base_skuid + '%'},
    )

    if q and q["results"]:
        for res in q["results"]:
            if res.get("mpn"):
                ids["mpn"].append(res.get("mpn"))
            if res.get("gtin"):
                ids["gtin"].append(res.get("gtin"))
            if res.get("brand"):
              ids["brand"] = res.get("brand")

    return ids

@cache.memoize()
def get_gtin(fullskuid):
    """get gtin for skuid

    Args:
      fullskuid (str): The fully-optioned skuid for the item, no dashes

    Returns:
      str: the mpn, if found, empty string otherwise
    """
    if not fullskuid or not isinstance(fullskuid, str):
        return ""

    # remove any dashes
    fullskuid = fullskuid.replace("-", "")
    res = DB.fetch_one(
        """
          SELECT upc AS mpn
          FROM product_metadata
          WHERE fullsku = %(fullskuid)s
        """,
        {"fullskuid": fullskuid},
    )

    return res.get("mpn") if res and res.get("mpn") else ""

@cache.memoize()
def get_vendor(fullskuid):
    """get vendor for skuid

    Args:
      fullskuid (str): The fully-optioned skuid for the item, no dashes

    Returns:
      str: the mpn, if found, empty string otherwise
    """
    if not fullskuid or not isinstance(fullskuid, str):
        return ""

    # remove any dashes
    fullskuid = fullskuid.replace("-", "")
    res = DB.fetch_one(
        """
          SELECT vendor
          FROM product_metadata
          WHERE fullsku = %(fullskuid)s
        """,
        {"fullskuid": fullskuid},
    )

    return res.get("vendor") if res and res.get("vendor") else current_app.config["STORE_NAME"]

@cache.memoize()
def get_attributes(fullskuid):
    """get product atttributes for skuid.

    Args:
      fullskuid (str): The fully-optioned skuid for the item

    Returns:
      dict: the attributes
    """
    if not fullskuid or not isinstance(fullskuid, str):
        return ""

    # remove any dashes
    fullskuid = fullskuid.replace("-", "")
    q = DB.fetch_all(
        """
          SELECT attribute_name, attribute_value
          FROM product_attributes
          WHERE fullskuid = %(fullskuid)s
        """,
        {"fullskuid": fullskuid},
    )['results']

    if not q:
      return {}

    attrs = {item['attribute_name']: item['attribute_value'] for item in q}
    return attrs

@cache.memoize()
def get_metadata(fullskuid):
  """Get the metadata record for a given skuid

  Args:
    fullskuid (str): The full skuid

  Returns:
    dict: the attributes
  """
  fullskuid = fullskuid.replace("-", "")
  q = DB.fetch_one(f"""
    SELECT *
    FROM product_metadata
    WHERE fullsku = %s
  """, (fullskuid))
  return q